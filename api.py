from bottle import Bottle, hook, post, request, response, route, run, static_file
import json
import os
import peewee as pw
from pathlib import Path
from playhouse.shortcuts import model_to_dict
from standardization import segmentation_standardization, classification_standardization
from settings import segmentationSettings, classificationSettings
from nii2png import convert
import gzip
import redis
import base64

from settings import initDefaultDB

db = pw.SqliteDatabase("data/image.db")
algo_seg = "segmentation"
algo_cla = "classification"
my_redis = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=6379, db=0)
pubsub = my_redis.pubsub(ignore_subscribe_messages=True)
pubsub.subscribe("covid-client")

img_folder = "images"
entry_folder = "entry-file"
covid_folder = "covid-case"
healthy_folder = "non-covid-case"
ready_clas_folder = "ready_for_classification"
ready_seg_folder = "ready_for_segmentation"


class JSONField(pw.TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class MedFile(pw.Model):
    pk = pw.AutoField()
    url = pw.CharField()
    path = pw.CharField()

    class Meta:
        database = db


class Status(pw.Model):
    pk = pw.AutoField()
    algotype = pw.CharField()
    files = pw.ManyToManyField(MedFile, backref="status")
    value = pw.BooleanField(default=False)
    results = JSONField(default=None, null=True)

    class Meta:
        database = db


FileAwaitingStatus = Status.files.get_through_model()

db.connect()
db.create_tables([MedFile, Status, FileAwaitingStatus])

# TODO migration
initDefaultDB()

@hook("after_request")
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "PUT, GET, POST, DELETE, OPTIONS"
    response.headers[
        "Access-Control-Allow-Headers"
    ] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization"


@route("/api/")
def root():
    return "This is the Datathon for COVID-19 API project"


@route("/api/upload", method=["OPTIONS", "POST"])
def upload():
    if request.method == "OPTIONS":
        return {}
    else:
        # Get the file
        upload = request.POST["file"]
        algorithm = request.POST["algorithm"]
        fname = Path(upload.filename)
        # If not a good format, return error
        if fname.suffix not in (".png", ".jpg", ".jpeg", ".nii", ".gz"):
            response.status = 405
            return {"message": "File extension not allowed.", "code": response.status}
        # Save the entry file
        save_path = Path(f"{img_folder}/{entry_folder}").resolve()
        if not save_path.exists():
            save_path.mkdir(parents=True)

        file_path = save_path / fname
        upload.save(str(file_path), True)

        if file_path.suffix == ".gz":
            tmp = gzip.decompress(file_path.read_bytes())
            tmpath = str(file_path.parent / file_path.stem)
            file_path.unlink()
            file_path = Path(tmpath)
            file_path.write_bytes(tmp)

        outputFiles = []
        if file_path.suffix == ".nii":
            outputFiles = convert(str(file_path), str(save_path))
            file_path.unlink()

        # Save it and get the new variables 'file_path'
        # Store url in db and return the result, these will be treated
        response.content_type = "application/json"
        if len(outputFiles) > 0:
            json_file_objs = []
            for filename in outputFiles:
                file_obj = saveStandardFile(filename, file_path, algorithm)
                if file_obj:
                    json_file_objs.append(file_obj)
            return json.dumps(json_file_objs)
        file_obj = saveStandardFile(file_path.name, file_path, algorithm)
        if file_obj:
            return json.dumps(file_obj)
        response.status = 500
        return {"message": "File could not be uploaded.", "code": response.status}


def saveStandardFile(filename, file_path, algorithm):
    writting_path = ""
    f_path = str(file_path.parent / filename)
    folder = classificationSettings["path"]
    if algorithm == algo_seg:
        folder = segmentationSettings["path"]
        file_url = segmentation_standardization(f_path)
        if file_url:
            writting_path = Path(file_url).resolve()
    else:
        file_url = classification_standardization(f_path)
        if file_url:
            writting_path = Path(file_url).resolve()
    if not writting_path == "":
        my_file = MedFile.create(
            url=f"/api/{folder}/{writting_path.name}", path=str(writting_path)
        )
        my_file.save()
        return model_to_dict(my_file)
    return False


# Make images available
@route("/api/images/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root=f"{img_folder}/")


#  Check status from redis
@route("/api/status", method=["OPTIONS", "POST"])
def status():
    if request.method == "OPTIONS":
        return {}
    else:
        statusKeys = json.loads(request.POST["statusKeys"])
        my_statuses = []
        for statusKey in statusKeys:
            if isinstance(statusKey, list):
                group_statuses = []
                for pk in statusKey:
                    group_statuses.append(checkStatus(pk))
                my_statuses.append(group_statuses)
            else:
                my_statuses.append(checkStatus(statusKey))
        return json.dumps(my_statuses)


def checkStatus(pk):
    my_status = Status.get(Status.pk == pk)
    if not my_status.value:
        message = pubsub.get_message()
        if message:
            my_message = json.loads(message["data"].decode())
            if my_message["id"] == pk:
                my_status.value = True
                my_status.results = saveResults(my_message["images"])
    return model_to_dict(my_status)


def saveResults(images):
    img_urls = []
    for imgData in images:
        source_file = MedFile.get(MedFile.pk == imgData["id"])
        source_url = Path(source_file.url)
        save_path = f"{img_folder}/{healthy_folder}"
        if "detect" in imgData["metadata"] and imgData["metadata"]["detect"]:
            save_path = f"{img_folder}/{covid_folder}"
        file_path = Path(f"{save_path}/res_{source_url.name}")
        file_path.write_bytes(base64.b64decode(imgData["binary"].encode()))
        img_urls.append(
            {
                "source": str(source_url),
                "result": f"/api/{str(file_path)}",
                "metadata": imgData["metadata"],
            }
        )
    return img_urls


@route("/api/classification", method=["OPTIONS", "POST"])
def classification():
    if request.method == "OPTIONS":
        return {}
    else:
        ids = json.loads(request.POST["ids"])
        response.content_type = "application/json"
        return json.dumps(handleAlgorithmCall(ids, algo_cla))


@route("/api/segmentation", method=["OPTIONS", "POST"])
def segmentation():
    if request.method == "OPTIONS":
        return {}
    else:
        ids = json.loads(request.POST["ids"])
        response.content_type = "application/json"
        return json.dumps(handleAlgorithmCall(ids, algo_seg))


def handleAlgorithmCall(ids, algo_type):
    resultingStatus = []
    for idData in ids:
        if isinstance(idData, list):
            resultingStatus.append(addStatus(idData, algo_type))
        else:
            resultingStatus.append(addStatus([idData], algo_type))
    return resultingStatus


def addStatus(ids, algo_type):
    my_status = Status.create(algotype=algo_type)
    my_status.save()
    med_files = MedFile.select().where(MedFile.pk << ids).execute()
    my_status.files.add(list(med_files))

    trigger_data = {"id": my_status.pk, "images": [], "algotype": algo_type}
    for med_file in med_files:
        encoded_string = ""
        image_file = Path(med_file.path)
        encoded_string = base64.b64encode(image_file.read_bytes())
        trigger_data["images"].append(
            {"id": med_file.pk, "binary": encoded_string.decode()}
        )
    topic = "covid-classification-server"
    if algo_type == algo_seg:
        topic = "covid-segmentation-server"
    my_redis.publish("covid-segmentation-server", json.dumps(trigger_data))
    return model_to_dict(my_status)


run(host="0.0.0.0", port=8000, debug=True)

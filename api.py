from bottle import Bottle, hook, post, request, response, route, run, static_file
import json
import peewee as pw
from pathlib import Path
from playhouse.sqlite_ext import JSONField
from playhouse.shortcuts import model_to_dict
from standardization import segmentation_standardization, classification_standardization
from settings import SegmentationSettings
from settings import ClassificationSettings
from nii2png import convert
import gzip
import redis

db = pw.SqliteDatabase("data/image.db")
# my_redis = redis.Redis(host='localhost', port=6379, db=0)
# pubsub = my_redis.pubsub()
# pubsub.subscribe("covid")

class MedFile(pw.Model):
    pk = pw.AutoField()
    url = pw.CharField()
    path = pw.CharField()

    class Meta:
        database = db

class Status(pw.Model):
    pk = pw.AutoField()
    images = pw.ManyToManyField(MedFile, backref='status')
    value = pw.BooleanField(default=False)
    results = JSONField()

    class Meta:
        database = db

FileAwaitingStatus = Status.images.get_through_model()

db.connect()
db.create_tables([MedFile, Status, FileAwaitingStatus])


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
    ] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"


@route("/")
def root():
    return "This is the Datathon for COVID-19 API project"


@route("/upload", method=["OPTIONS", "POST"])
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
        save_path = Path("images/entry-file").resolve()
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
    folder = ClassificationSettings.path
    if algorithm == "segmentation":
        folder = SegmentationSettings.path
        file_url = segmentation_standardization(f_path)
        if file_url:
            writting_path = Path(file_url).resolve()
    else:
        file_url = classification_standardization(f_path)
        if file_url:
            writting_path = Path(file_url).resolve()
    if not writting_path == "":
        my_file = MedFile.create(
            url=f"/{folder}/{writting_path.name}", path=str(writting_path)
        )
        my_file.save()
        return model_to_dict(my_file)
    return False

# Make images available
@route("/images/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root="images/")

#  Check status from redis
@route("/status", method=["OPTIONS", "GET"])
def status():
    if request.method == "OPTIONS":
        return {}
    else:
        pass
        # statusKey = request.POST["statusKey"]
        # my_status = Status.get(Status.pk == statusKey)
        # if not my_status.value:
        #     message = pubsub.get_message()
        #     if message:
        #         my_message = json.loads(message['data'].decode("utf-8"))
        #         if my_message['id'] == statusKey:
        #             my_status.value = True
        #             my_status.result = my_message['images']
        # return json.dumps(model_to_dict(my_status))

@route("/classification", method=["OPTIONS", "POST"])
def classification():
    if request.method == "OPTIONS":
        return {}
    else:
        ids = request.POST["ids"]
        # Start classification
        # Save the initial status
        my_status = addStatus(ids)
        response.content_type = "application/json"
        return json.dumps(model_to_dict(my_status))


@route("/segmentation", method=["OPTIONS", "POST"])
def segmentation():
    if request.method == "OPTIONS":
        return {}
    else:
        ids = request.POST["ids"]
        print("ids", ids)
        for pk in ids:
            print("pks", MedFile.get(MedFile.pk == pk))
        # Do segmentation
        # Save the images
        my_status = addStatus(ids)
        response.content_type = "application/json"
        return json.dumps(model_to_dict(my_status))

def handleAlgorithmCall(ids):
    my_status = addStatus(ids)
    return json.dumps(model_to_dict(my_status))

def addStatus(ids):
    my_status = Status.create()
    my_status.files.add(MedFile.select().where(MedFile.pk << ids))
    my_status.save()
    return my_status

run(host="0.0.0.0", port=8000, debug=True)

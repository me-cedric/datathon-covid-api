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
my_redis = redis.Redis(host='localhost', port=6379, db=0)
pubsub = my_redis.pubsub()
pubsub.subscribe("covid")

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
        if fname.suffix not in (".png", ".jpg", ".jpeg", ".nii", ".nii.gz"):
            response.status = 405
            return {"message": "File extension not allowed.", "code": response.status}
        if fname.suffix == ".nii.gz":
            upload = gzip.GzipFile(fileobj=upload, mode='rb')
            fname = Path(upload.filename)
        # Save the entry file
        save_path = Path("images/entry-file").resolve()
        if not save_path.exists():
            save_path.mkdir(parents=True)

        file_path = save_path / fname
        upload.save(str(file_path), True)
        
        if fname.suffix == ".nii":
            convert(str(file_path), str(save_path))

        # TODO: Edit the image
        writting_path = ""
        # Save it and get the new variables 'file_path'
        # Store url in db and return the result, these will be treated
        folder = ClassificationSettings.path
        if algorithm == "segmentation":
            folder = SegmentationSettings.path
            writting_path = Path(segmentation_standardization(file_path)).resolve()
        else:
            writting_path = Path(classification_standardization(file_path)).resolve()
        my_file = MedFile.create(
            url=f"/{folder}/{writting_path.name}", path=str(writting_path)
        )
        my_file.save()
        response.content_type = "application/json"
        return json.dumps(model_to_dict(my_file))


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
        statusKey = request.POST["statusKey"]
        my_status = Status.get(Status.pk == statusKey)
        if not my_status.value:
            message = pubsub.get_message()
            if message:
                my_message = json.loads(message['data'].decode("utf-8"))
                if my_message['id'] == statusKey:
                    my_status.value = True
                    my_status.result = my_message['images']
        return json.dumps(model_to_dict(my_status))

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

def addStatus(ids):
    my_status = Status.create()
    my_status.files.add(MedFile.select().where(MedFile.pk << ids))
    my_status.save()
    return my_status

run(host="0.0.0.0", port=8000, debug=True)

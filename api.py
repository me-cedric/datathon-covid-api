from bottle import Bottle, post, request, route, run, static_file
import json
import peewee as pw

db = pw.SqliteDatabase("image.db")


class File(pw.Model):
    pk = pw.AutoField()
    url = pw.CharField()
    path = pw.CharField()

    class Meta:
        database = db


db.connect()
db.create_tables([File])


@route("/")
def root():
    assert [f for f in File.select()]
    return "This is the Datathon for COVID-19 API project"


@post("/upload")
def upload():
    # Get the file
    upload = request.forms.get("file")
    fname = Path(upload.filename)
    # If not a good format, return error
    if fname.suffix not in (".png", ".jpg", ".jpeg", ".nii", ".nii.gz"):
        response.status = 405
        return {"message": "File extension not allowed.", "code": response.status}

    # TODO: Edit the image

    # Save the entry file
    save_path = Path("images/entry-file").resolve()
    if not save_path.exists():
        save_path.mkdir(parents=True)

    file_path = save_path / fname
    upload.save(str(file_path))
    # Store url in db and return the result
    my_file = File.create(url="/img/" + str(file_path), path=str(file_path))
    return json.dumps(pw.model_to_dict(my_file))


# Make images available
@route("/img/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root="images/entry-file")


@post("/classification")
def classification():
    ids = request.forms.get("ids")
    # Do classification
    # Save the images
    image_urls = [
        {"type": "group", "urls": "/", "result": False, "accuracy": 95},
        {"type": "single", "url": "/", "result": True, "accuracy": 95},
    ]
    response.content_type = "application/json"
    return json.dumps(image_urls)


@post("/segmentation")
def segmentation():
    ids = request.forms.get("ids")
    # Do segmentation
    # Save the images
    image_urls = [
        {"type": "group", "urls": "/", "accuracy": 95},
        {"type": "single", "url": "/", "accuracy": 95},
    ]
    response.content_type = "application/json"
    return json.dumps(image_urls)


run(host="localhost", port=8080, debug=True)

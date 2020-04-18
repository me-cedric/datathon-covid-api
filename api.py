from bottle import Bottle, hook, post, request, response, route, run, static_file
import json
import peewee as pw
from pathlib import Path
from playhouse.shortcuts import *

db = pw.SqliteDatabase("data/image.db")

class MedFile(pw.Model):
    pk = pw.AutoField()
    url = pw.CharField()
    path = pw.CharField()

    class Meta:
        database = db

db.connect()
db.create_tables([MedFile])

@hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@route('/')
def root():
    return 'This is the Datathon for COVID-19 API project'

@route('/upload', method=['OPTIONS', 'POST'])
def upload():
    if request.method == 'OPTIONS':
        return {}
    else:
        # Get the file
        upload = request.POST['file']
        fname = Path(upload.filename)
        # If not a good format, return error
        if fname.suffix not in (".png", ".jpg", ".jpeg", ".nii", ".nii.gz"):
            response.status = 405
            return {"message": "File extension not allowed.", "code": response.status}

        # Save the entry file
        save_path = Path('images/entry-file').resolve()
        if not save_path.exists():
            save_path.mkdir(parents=True)

        file_path = save_path / fname
        upload.save(str(file_path), True)

        # TODO: Edit the image
        # Save it and get the new variables 'file_path'
        # Store url in db and return the result, these will be treated
        my_file = MedFile.create(url='/img/' + str(file_path), path=str(file_path))
        return json.dumps(model_to_dict(my_file))


# Make images available
@route('/img/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root="images/entry-file")

@route('/classification', method=['OPTIONS', 'POST'])
def classification():
    if request.method == 'OPTIONS':
        return {}
    else:
        ids = request.POST['ids']
        # Do classification
        # Save the images
        image_urls = [
            {"type": "group", "urls": "/", "result": False, "accuracy": 95},
            {"type": "single", "url": "/", "result": True, "accuracy": 95},
        ]
        response.content_type = 'application/json'
        return json.dumps(image_urls)

@route('/segmentation', method=['OPTIONS', 'POST'])
def segmentation():
    if request.method == 'OPTIONS':
        return {}
    else:
        ids = request.POST['ids']
        print('ids', ids)
        for pk in ids:
            print('pks', MedFile.get(MedFile.pk == pk))
        # Do segmentation
        # Save the images
        image_urls = [
            {"type": "group", "urls": "/", "accuracy": 95},
            {"type": "single", "url": "/", "accuracy": 95},
        ]
        response.content_type = 'application/json'
        return json.dumps(model_to_dict(image_urls))

run(host='0.0.0.0', port=8000, debug=True)

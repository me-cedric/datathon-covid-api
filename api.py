import os
from bottle import post, request, route, run, static_file
from json import dumps

@route('/')
def root():
    return "This is the Datathon for COVID-19 API project"

@post('/upload')
def upload():
    # Get the file
    file = request.forms.get('file')
    name, ext = os.path.splitext(upload.filename)
    # If not a good format, return error
    if ext not in ('.png', '.jpg', '.jpeg', '.nii', '.nii.gz'):
        response.status = 405
        return "File extension not allowed."

    # TODO: Edit the image

    # Save the entry file
    save_path = "/entry-file"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_path = "{path}/{file}".format(path=save_path, file=upload.filename)
    upload.save(file_path)

    return file

# Make images available
@route('/img/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='entry-file')

@post('/classification')
def classification():
    ids = request.forms.get('ids')
    # Do classification
    # Save the images
    image_urls = [{ "type": "group", "urls": "/", "result": False, "accuracy": 95 }, { "type": "single", "url": "/", "result": True, "accuracy": 95 }]
    response.content_type = 'application/json'
    return dumps(image_urls)

@post('/segmentation')
def segmentation():
    ids = request.forms.get('ids')
    # Do segmentation
    # Save the images
    image_urls = [{ "type": "group", "urls": "/", "accuracy": 95 }, { "type": "single", "url": "/", "accuracy": 95 }]
    response.content_type = 'application/json'
    return dumps(image_urls)
    
run(host='localhost', port=8080, debug=True)
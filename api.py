import os
from bottle import post, request, route, run, static_file

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
    return "Hello World!"

@post('/segmentation')
def segmentation():
    ids = request.forms.get('ids')
    return "Hello World!"
    
run(host='localhost', port=8080, debug=True)
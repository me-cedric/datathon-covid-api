import os
from bottle import post, request, route, run

@route('/')
def root():
    return "This is the Datathon for COVID-19 API project"

@post('/upload')
def upload():
    file = request.forms.get('file')
    return file

@post('/classification')
def classification():
    ids = request.forms.get('ids')
    return "Hello World!"

@post('/segmentation')
def segmentation():
    ids = request.forms.get('ids')
    return "Hello World!"
    
run(host='localhost', port=8080, debug=True)
# -*-coding:Latin-1 -*

# Extern packages
import numpy
import cv2
import peewee as pw
import json


class JSONField(pw.TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


db = pw.SqliteDatabase("data/image.db")

# Segmentation class and wrapper
segmentationSettings = {
    "path": "images/ready_for_segmentation/",
    "width": 512,
    "height": 512,
    "format": ".png",
    "color": cv2.IMREAD_GRAYSCALE,
    "interpolation": cv2.INTER_AREA,
}


class AlgoSettings(pw.Model):
    name = pw.CharField(unique=True)
    jsonFile = JSONField(default=None)

    class Meta:
        database = db
        table_name = "AlgoSettings"


# Classification class and wrapper
classificationSettings = {
    "path": "images/ready_for_classification/",
    "width": 416,
    "height": 416,
    "format": ".jpg",
    "color": cv2.IMREAD_GRAYSCALE,
    "interpolation": cv2.INTER_AREA,
}


def initDefaultDB():
    db.connect()  # Maybe we should test if connection is OK
    db.create_tables([AlgoSettings])
    # If default models don't exist -> add the row to table
    addSettings("segmentation", segmentationSettings)
    addSettings("classification", classificationSettings)
    db.close()


# Create a new row
def addSettings(seg_name, seg_set):
    try:
        exist = AlgoSettings.select().where(AlgoSettings.name == seg_name).get()
    except AlgoSettings.DoesNotExist:
        row = AlgoSettings.create(name=seg_name, jsonFile=seg_set)
        row.save()


# Edit an existing row
def editSettings(seg_name, seg_set):
    try:
        exist = AlgoSettings.select().where(AlgoSettings.name == seg_name).get()
    except AlgoSettings.DoesNotExist:
        return
    query = AlgoSettings.update({AlgoSettings.jsonFile: seg_set}).where(name=seg_name)
    query.execute()


# Delete existing row
def deleteSettings(seg_name):
    try:
        exist = AlgoSettings.select().where(AlgoSettings.name == seg_name).get()
    except AlgoSettings.DoesNotExist:
        return

    exist.delete_instance()

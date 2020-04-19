# -*-coding:Latin-1 -*

# Extern packages
import numpy
import cv2
import peewee
import json

db = peewee.SqliteDatabase("data/image.db")

# Segmentation class and wrapper
class SegmentationSettings :
	name = "default"
    path = "images/ready_for_segmentation/"
    width = 512
    height = 512
    format = ".png"
    color = cv2.IMREAD_GRAYSCALE
    interpolation = cv2.INTER_AREA
	
class SegmentationModel ( Model ) :
	name = CharField ( unique = True )
	jsonFile = JSONField()
	
	class Meta :
		database = db
		table_name = "SegmentationSettings"

		
# Classification class and wrapper
class ClassificationSettings :
	name = "default"
    path = "images/ready_for_classification/"
    width = 416
    height = 416
    format = ".jpg"
    color = cv2.IMREAD_GRAYSCALE
    interpolation = cv2.INTER_AREA

class ClassificationModel ( Model ) :
	name = CharField ( unique = True )
	jsonFile = JSONField()
	
	class Meta :
		database = db
		table_name = "ClassificationSettings"
				

def initDefaultDB ( ) :
	db.connect() # Maybe we should test if connection is OK
	
	# If tables don't exist -> create them
	if ( ! peewee.table_exists ( SegmentationSettings.Meta.table_name ) ) :
		db.create_tables( SegmentationModel )
		
	if ( ! peewee.table_exists ( ClassificationSettings.Meta.table_name ) ) :
		db.create_tables( ClassificationModel )
	
	# If default models don't exist -> add the row to table
	addSegmentationSettings   ( "default", SegmentationSettings() )
	addClassificationSettings ( "default", ClassificationSettings() )
		
	db.close()
	
# Create a new row
def addSegmentationSettings ( str_name, seg_set ) :
	try :
		exist = SegmentationModel.select().where( SegmentationModel.name == str_name ).get()
		
	except SegmentationModel.DoesNotExist :
		jsf = json.dumps ( seg_set.__dict__ )
		row = SegmentationModel ( name = str_name, jsonFile = jsf )
		row.save()

def addClassificationSettings ( str_name, class_set ) :
	try :
		exist = ClassificationModel.select().where( ClassificationModel.name == str_name ).get()
		
	except ClassificationModel.DoesNotExist :
		jsf = json.dumps ( class_set.__dict__ )
		row = ClassificationModel ( name = str_name, jsonFile = jsf )
		row.save()

# Edit an existing row
def editSegmentationSettings ( str_name, seg_set ) :
	try :
		exist = SegmentationModel.select().where( SegmentationModel.name == str_name ).get()
	except SegmentationModel.DoesNotExist :
		return
	
	jsf = json.dumps ( seg_set.__dict__ )
	query = SegmentationModel.update ( { SegmentationModel.jsonFile : jsf } ).where( name = str_name )
	query.execute()
	
def editClassificationSettings ( str_name, seg_set ) :
	try :
		exist = ClassificationModel.select().where( ClassificationModel.name == str_name ).get()
	except ClassificationModel.DoesNotExist :
		return
	
	jsf = json.dumps ( seg_set.__dict__ )
	query = ClassificationModel.update ( { ClassificationModel.jsonFile : jsf } ).where( name = str_name )
	query.execute()

# Delete existing row		
def deleteSegmentationSettings ( str_name ) :
	try :
		exist = SegmentationModel.select().where( SegmentationModel.name == str_name ).get()
	except SegmentationModel.DoesNotExist :
		return
	
	exist.delete_instance()
	
def deleteClassificationSettings ( str_name ) :
	try :
		exist = ClassificationModel.select().where( ClassificationModel.name == str_name ).get()
	except ClassificationModel.DoesNotExist :
		return
	
	exist.delete_instance()

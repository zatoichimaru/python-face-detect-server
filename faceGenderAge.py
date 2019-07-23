#!/usr/bin/env python3
import numpy as np
import cv2
import imutils
import os
import hashlib
import time
import json
import zipfile 
import shutil
import codecs
import sys
import pymysql
from datetime import datetime
from random import randint

#Path
pathRoot = os.getcwd()
pathOpencv = os.path.dirname(cv2.__file__)
source = os.path.join( pathRoot, 'upload' )
destination = os.path.join( source, 'filesTemp' )
source = os.path.join( source, 'files.zip' )

face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_alt.xml')

def generateRandomHashName():
    hashValue = hashlib.sha1( str( datetime.now() ).encode('utf-8') ).hexdigest()
    return hashValue

def generateFolderDefault():
    folderName = 'files'

    if not os.path.exists( os.path.join( pathRoot, folderName ) ):
        os.makedirs( os.path.join( pathRoot, folderName ) )
    
    return os.path.normpath( os.path.join( pathRoot, folderName ) )

def generateFolderPeople( fileName, pathValue ):
    if( not os.path.exists( os.path.join( pathValue, fileName ) ) ):
        os.makedirs( os.path.join( pathValue, fileName ) )
    
    return  os.path.normpath( os.path.join( pathValue, fileName ) )

def unziperFile( source, destination ):
	try:
		if os.path.exists( source ):
			zf = zipfile.ZipFile( source )
			zf.extractall( destination )
			zf.close()
		
			#os.remove( source )
	finally:
		print('--------Unzip Done ---------')

def initialize_caffe_models():
	age_net = cv2.dnn.readNetFromCaffe(
		'data/deploy_age.prototxt', 
		'data/age_net.caffemodel')

	gender_net = cv2.dnn.readNetFromCaffe(
		'data/deploy_gender.prototxt', 
		'data/gender_net.caffemodel')

	return(age_net, gender_net)

def read_from_camera(age_net, gender_net, destination):
	font = cv2.FONT_HERSHEY_SIMPLEX
	filePath = ''
	imagemPath = ''

	for root, dirs, files in os.walk( destination ):
		for fileName in files:
			if fileName.endswith(".png"):
				imagemPath = os.path.join( root, fileName )

			image = cv2.imread( imagemPath )
		
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			faces = face_cascade.detectMultiScale(gray, 1.1, 5)

			if not np.any(faces):
				continue

			for (x, y, w, h) in faces:
				cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)

				# Get Face 
				face_img = image[y:y+h, h:h+w].copy()
				blob = cv2.dnn.blobFromImage(face_img, 1, (227, 227), MODEL_MEAN_VALUES, swapRB=False)

				#Predict Gender
				gender_net.setInput(blob)
				gender_preds = gender_net.forward()
				gender = gender_list[gender_preds[0].argmax()]
				#print("Gênero : " + gender)

				#Predict Age
				age_net.setInput(blob)
				age_preds = age_net.forward()
				age = age_list[age_preds[0].argmax()]
				#print("Idade: " + age)

				overlay_text = "%s %s" % (gender, age)
				cv2.putText(image, overlay_text, (x, y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


				jsonFileLoad = openJsonArray( os.path.join( root, 'file.json' ) )
				
				for jsonValue in jsonFileLoad:
					if jsonValue.get('image') == fileName:
						face_position_x = str(x)
						face_position_y = str(y)
						face_position_width = str(w)
						face_position_height = str(h)
						face_position_gender = str(gender)
						face_position_age = str(age)
						face_position_image = str(jsonValue.get('image'))
						face_position_porcentage = str(randint(30, 80))
						face_position_wait = str(jsonValue.get('minute')) +':'+ str(jsonValue.get('second'))
						face_position_create = str(jsonValue.get('datetime'))

				#		#inserir os valores no banco
						insertFace(face_position_x, face_position_y, face_position_width, face_position_height, face_position_gender, face_position_age, face_position_porcentage, face_position_wait, face_position_image, face_position_create)

			#cv2.imshow('frame', image)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

		#time.sleep(1)

def openJsonArray( filename ):
	file = open( filename ).read().encode("utf-8")
	return json.loads( file )


def insertFace(face_position_x, face_position_y, face_position_width, face_position_height, face_position_gender, face_position_age, face_position_porcentage, face_position_wait, face_position_image, face_position_create):
    connect = pymysql.connect( host="poc.ci9niqaqsefm.us-east-1.rds.amazonaws.com", user= "jump", passwd="jump1234", db="poc" )
    cursorQuery = connect.cursor()

    sql = "INSERT INTO face_position (face_position_x,face_position_y,face_position_width,face_position_height,face_position_gender,face_position_age,face_position_porcentage, face_position_wait, face_position_image, face_position_create) VALUES ('" + face_position_x + "','"+ face_position_y + "','"+ face_position_width + "','"+ face_position_height + "','"+ face_position_gender + "','"+ face_position_age + "','"+ face_position_porcentage + "','"+ face_position_wait + "','"+ face_position_image + "','"+ face_position_create + "')"
    cursorQuery.execute( sql )
    id = cursorQuery.lastrowid

    if( id ):
        print('Incluido com sucesso')

    connect.commit()
    connect.close()

if __name__ == "__main__":

	MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
	age_list = ['(0, 2)', '(4, 6)', '(8, 12)', '(15, 20)', '(25, 32)', '(38, 43)', '(48, 53)', '(60, 100)']
	gender_list = ['Homem', 'Mulher']


	unziperFile( source, os.path.join( pathRoot, 'upload' ) )
	age_net, gender_net = initialize_caffe_models()
	read_from_camera(age_net, gender_net, destination )

	if not os.path.exists( os.path.join( pathRoot, 'files' ) ):
		shutil.rmtree( destination )

	if not os.path.exists( os.path.join( pathRoot, 'files.zip' ) ):
		renameZip = 'files_' + time.strftime( "%Y%m%d" ) + '_' + time.strftime( "%H%M%S" )
		os.rename( source, source.replace( "files", renameZip) )




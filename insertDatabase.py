#!/usr/bin/env python3
import pymysql

def insertFace(face_position_x, face_position_y, face_position_width, face_position_height, face_position_gender, face_position_age, face_position_porcentage):
    connect = pymysql.connect( host="poc.ci9niqaqsefm.us-east-1.rds.amazonaws.com", user= "jump", passwd="jump1234", db="poc" )
    cursorQuery = connect.cursor()

    sql = "INSERT INTO face_position (face_position_x,face_position_y,face_position_width,face_position_height,face_position_gender,face_position_age,face_position_porcentage) VALUES ('" + face_position_x + "','"+ face_position_y + "','"+ face_position_width + "','"+ face_position_height + "','"+ face_position_gender + "','"+ face_position_age + "','"+ face_position_porcentage + "')"
    cursorQuery.execute( sql )
    id = cursorQuery.lastrowid

    if( id ):
        print('Incluido com sucesso')

    connect.commit()
    connect.close()


face_position_x = '11111111111'
face_position_y = '22222222222'
face_position_width = '33333333333'
face_position_height = '44444444444'
face_position_gender = 'Masculino'
face_position_age = '34'
face_position_porcentage = '99.0'

#inserir os valores no banco
insertFace(face_position_x, face_position_y, face_position_width, face_position_height, face_position_gender, face_position_age, face_position_porcentage)

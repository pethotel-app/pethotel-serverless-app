from datetime import datetime
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource
from config import Config
from mysql_connection import get_connection
from mysql.connector import Error
from email_validator import validate_email, EmailNotValidError
from utils import check_password, hash_password
from datetime import datetime
import boto3

class PetListResource(Resource) : 
    # 반려동물 등록 API
    @jwt_required()
    def post(self) :

        user_id = get_jwt_identity()

        if 'photo' not in request.files :
            return {'error' : '사진데이터 필수'}, 400
        
        file = request.files['photo']
        name = request.form['name']
        classification = request.form['classification']
        species = request.form['species']
        age = request.form['age']
        weight = request.form['weight']
        gender = request.form['gender']

        if 'image' not in file.content_type :
            return {'error' : '이미지 파일이 아닙니다.'}
        
        # 사진 S3에 저장
        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(':', '_') + '.jpg'
        file.filename = new_file_name

        client = boto3.client('s3', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

        try :
            client.upload_fileobj(file, Config.S3_BUCKET, new_file_name, ExtraArgs= {'ACL' : 'public-read', 'ContentType' : file.content_type})
        
        except Exception as e :
            return {"error" : str(e)}, 500

        # 저장된 사진의 imgUrl
        imgUrl = Config.S3_LOCATION + new_file_name

        
        try :
            connection = get_connection()

            query = '''insert into pet
                    (userId, name, classification, species, age, weight, gender, petImgUrl)
                    values
                    (%s, %s, %s, %s, %s, %s, %s, %s);'''
            
            record = ( user_id, name, classification, species, age, weight, gender, imgUrl )

            cursor=connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return{"result" : "fail", "error" : str(e)} , 500

        return {"result" : "success"} , 200
    
    # 반려동물 조회 API
    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select id,userId,petImgUrl,name,classification,species,age,weight,gender
                    from pet
                    where userId=%s;'''

            ## 중요!!!! select 문은 
            ## 커서를 가져올 때 dictionary = True로 해준다
            cursor = connection.cursor(dictionary=True)

            record = (user_id,)

            cursor.execute(query, record)

            result_list=cursor.fetchall()

            print(result_list)
            


            cursor.close()
            connection.close()
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{"result":"fail","error":str(e)}, 500
        
        return {"result" : 'success','items':result_list,'count':len(result_list)}, 200

class PetResource(Resource) :
    # 반려동물 수정 API
    @jwt_required()
    def put(self, petId) :

        user_id = get_jwt_identity()
        
        name = request.form['name']
        classification = request.form['classification']
        species = request.form['species']
        age = request.form['age']
        weight = request.form['weight']
        gender = request.form['gender']
        petImgUrl = request.form['petImgUrl']

        if 'photo' in request.files:
            file = request.files['photo']

            if file :
                # 파일이 있는 경우 처리할 코드 작성
                current_time = datetime.now()
                new_file_name = current_time.isoformat().replace(':', '_') + '.jpg'
                file.filename = new_file_name

                client = boto3.client('s3', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

                try :
                    content_type = file.content_type if file.content_type else 'image/jpeg'
                    client.upload_fileobj(file, Config.S3_BUCKET, new_file_name, ExtraArgs= {'ACL' : 'public-read', 'ContentType' : content_type})
                
                except Exception as e :
                    return {"error" : str(e)}, 500

                # 저장된 사진의 imgUrl
                imgUrl = Config.S3_LOCATION + new_file_name

            else :
                # 파일이 없는 경우 처리할 코드 작성
                imgUrl = petImgUrl

            try :
                connection = get_connection()
                query = '''update pet
                        set name = %s,
                        classification = %s,
                        species = %s,
                        age = %s,
                        weight = %s,
                        gender = %s,
                        petImgUrl = %s
                        where id = %s and userId = %s;'''
                
                record = (name, classification, species, age, weight, gender, imgUrl, petId, user_id)
                
                cursor = connection.cursor()

                cursor.execute(query, record)

                connection.commit()

                cursor.close()
                connection.close()

            except Error as e :
                print(e)
                cursor.close()
                connection.close()
                return {'result' : 'fail', 'error' : str(e)}, 500

            return {'result' : 'success' }, 200

    # 반려동물 삭제 API
    @jwt_required()
    def delete(self,petId) :

        user_id=get_jwt_identity()

        try :
            connection = get_connection()
            query = '''delete from pet
                    where id = %s and userId = %s;'''
            record = (petId,user_id)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()
            connection.close()
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'result':'fail','error':str(e)}, 500

        return {'result':'success'},200
    

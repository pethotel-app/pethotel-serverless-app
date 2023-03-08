from flask import request
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

class PetListResource(Resource) : 
    # 반려동물 등록 API
    @jwt_required()
    def post(self) :




        # 1. 클라이언트가 보내준 데이터가 있으면
        #    그 데이터를 받아준다.
        data = request.get_json()

        # 1-1 헤더에JWT 토큰이 있으면 토큰 정보를 받아준다
        user_id = get_jwt_identity()



        # 2. 이 레시피정보를 DB에 저장해야한다.
        
        try :
            ### 1. DB에 연결
            connection = get_connection()

            ### 2. 쿼리문 만들기
            # todo : image처리
            query = '''insert into pet
                    (userId,name,classification,species,age,weight,gender)
                    values
                    (%s,%s,%s,%s,%s,%s,%s);'''
            ### 3. 쿼리에 매칭되는 변수 처리 해준다. 튜플로!
            record = ( user_id,data['name'],data['classification'],
                      data['species'],data['age'],data['weight'],data['gender'] )

            ### 4. 커서를 가져온다.
            cursor=connection.cursor()

            ### 5. 쿼리문을 커서로 실행한다.
            cursor.execute(query, record)

            ### 6. 커밋을 해줘야 DB에 완전히 반영된다.
            connection.commit()

            ### 7. 자원 해제
            cursor.close()
            connection.close()

        except Error as e :

            print(e)
            cursor.close()
            connection.close()

            return{"result" : "fail", "error" : str(e)} , 500



        # API를 끝낼때는
        # 클라이언트에 보내줄 정보(json)와 http 상태 코드를
        # 리턴한다.
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


        data = request.get_json()

        user_id = get_jwt_identity()

        ### todo : 이미지 처리
        try :
            connection = get_connection()
            query = '''update pet
                    set name = %s,
                    classification = %s,
                    species = %s,
                    age = %s,
                    weight = %s,
                    gender = %s
                    where id = %s and userId = %s;'''
            
            record = (data['name'],data['classification'],data['species'],data['age'],
                      data['weight'],data['gender'],petId,user_id)
            
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
    

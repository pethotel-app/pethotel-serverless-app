
from flask import request
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

class ReservationResource(Resource) : 
    
    # 내 예약 정보 가져오는 API 
    # 18번째 화면 기획서
    @jwt_required()
    def get(self) :
        user_id=get_jwt_identity()

        # 2. db에 저장된 데이터를 가져온다.
        try :
            connection = get_connection()

            query = '''select r.*,h.title,p.name
                    from reservations r
                    left join hotel h
                    on h.id = r.hotelId
                    left join pet p
                    on p.id = r.petId
                    where r.userId = %s
                    order by r.checkOutDate desc;'''
            record = (user_id,)

            ## 중요!!!! select 문은 
            ## 커서를 가져올 때 dictionary = True로 해준다
            cursor = connection.cursor(dictionary=True)

            cursor.execute(query,record)

            result_list=cursor.fetchall()

            print(result_list)
            
            # datetime은 json으로 보낼 수 없다.
            # 따라서 시간을 문자열로 변환해서 보내준다.
            i = 0
            for row in result_list :
                result_list[i]['checkInDate']=row['checkInDate'].isoformat()
                result_list[i]['checkOutDate']=row['checkOutDate'].isoformat()
                result_list[i]['createdAt']=row['createdAt'].isoformat()
                result_list[i]['updatedAt']=row['updatedAt'].isoformat()
                i = i+1

            cursor.close()
            connection.close()
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{"result":"fail","error":str(e)}, 500
        
        return {"result" : 'success','items':result_list,'count':len(result_list)}, 200

    # 예약 정보 저장 ( 생성 )하는 API
    # 28번째 화면 기획서
    @jwt_required()
    def post(self) :
        data = request.get_json()
        user_id=get_jwt_identity()

        try :
            ### 1. DB에 연결
            connection = get_connection()
            connection.begin()

            ### 2. 쿼리문 만들기
            query = '''insert into reservations
                    (petId,userId,hotelId,checkInDate,checkOutDate,content,price)
                    values
                    (%s,%s,%s,%s,%s,%s,%s);'''
            ### 3. 쿼리에 매칭되는 변수 처리 해준다. 튜플로!
            record = ( data['petId'],user_id,data['hotelId'],
                      data['checkInDate'],data['checkOutDate'],data['content'],data['price'] )

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

            connection.rollback()

            print(e)
            cursor.close()
            connection.close()

            return{"result" : "fail", "error" : str(e)} , 500



        # API를 끝낼때는
        # 클라이언트에 보내줄 정보(json)와 http 상태 코드를
        # 리턴한다.
        return {"result" : "success"} , 200
    
   
    
    # 취소 사유, 금액
    @jwt_required()
    def put(self) :
        data = request.get_json()
        userId = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into cancelReason(userId, hotelId,reason,cancelPrice,resCreatedAt)
                        values(%s,%s,%s,%s,%s);'''

            record = (userId,data['hotelId'], data['reason'],data['cancelPrice'],data['resCreatedAt'])

            cursor = connection.cursor()
            cursor.execute(query,record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:

            print(e)
            cursor.close()
            connection.close()

            return{"result" : "fail" , "error" : str(e)}, 500
        
        return {"result" : "success"}, 200
    
class CancelReservationResource(Resource) :
    
    @jwt_required()
    def delete(self,hotelId,petId) :
        userId = get_jwt_identity()


        try :
            connection = get_connection()
            connection.begin()

            query =  '''delete from reservations
                    where userId=%s and hotelId = %s and petId =%s;'''
            
            record = (userId, hotelId,petId)

            cursor = connection.cursor()
            cursor.execute(query,record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            connection.rollback()
            print(e)
            cursor.close()
            connection.close()

            return{"result" : "fail", "error" : str(e)}, 500
        
        return{"result" : "success"} , 200

    

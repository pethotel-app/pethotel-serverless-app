from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

# 유저 포인트 조회
class PointSearchResource(Resource) :
    @jwt_required()
    def get(self) :

        userId = get_jwt_identity()

        try :

            connection = get_connection()

            query = '''select p.content, p.addPoint, p.totalPoint,p.createdAt from points p
                    join user u
                    on p.userId = u.id
                    where u.id = %s;'''
            
            record = (userId,)

            cursor = connection.cursor(dictionary=True)


            cursor.execute(query,record)

            resultList = cursor.fetchall()

            i = 0
            for row in resultList :
                resultList[i]['createdAt'] = row['createdAt'].isoformat()
                i = i + 1


            cursor.close()
            connection.close()

        except Error as e :


            cursor.close()
            connection.close()

            return{'error' : str(e)}, 500

        if len(resultList) == 0 :

            return {'error' : '잘못된 유저 아이디입니다.'}, 400

        return{'result' : 'success', 'items' : resultList}

# 유저 포인트 적립
class PointAddResource(Resource) : 
    @jwt_required()
    def post(self) :
        

        data = request.get_json()
        
        
        userId = get_jwt_identity()

        try : 
            connection = get_connection()

            query = '''insert into points
                    (userId, content, addPoint)
                    Values (%s, %s, %s);'''

            record = (userId,data['content'],data['addPoint'])

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            
            print(e)
            cursor.close()
            connection.close()
            
            return{"result" : 'fail','error' : str(e)}, 500

        return {"result" : "success"} , 200
    



# 쿠폰조회
class CouponSearchResource(Resource) :
    @jwt_required()
    def get(self) :

        userId = get_jwt_identity()


        try : 
            connection = get_connection()
            
            query = '''select userId,couponId,title,description,dateOfUseStart,dateOfUseEnd from coupons c
                    join checkCoupon k
                    on c.id = k.couponId
                    where userId = %s;'''

            record = (userId,)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query , record)
            
            resultList = cursor.fetchall()

            i = 0
            for row in resultList :
                resultList[i]['dateOfUseStart'] = row['dateOfUseStart'].isoformat()
                resultList[i]['dateOfUseEnd'] = row['dateOfUseEnd'].isoformat()
                i = i + 1

     
            cursor.close()
            connection.close()

        except Error as e :
            
            print(e)
            
            cursor.close()
            connection.close()
            return{'error' : str(e)}, 500
        
        
        return{'result' : 'success' , 'couponList' : resultList, 'count' : len(resultList)}

# 쿠폰 사용
class CouponUseResource(Resource) :
    @jwt_required()
    def delete(self,couponId) :

        userId = get_jwt_identity()

        try : 
            connection = get_connection()
            
            query = '''delete from checkCoupon
                    where UserId= %s and couponId= %s;'''

            record = (userId,couponId)

            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()
            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {'error':str(e)},500

        return {'result':'success'},200
    

    






            





            



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
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :

            connection = get_connection()

            query = '''select p.content, p.addPoint, p.totalPoint,p.createdAt,IF(p.addPoint > 0, 1, 0) AS isEarn
                    from points p
                    join user u
                    on p.userId = u.id
                    where u.id = %s
                    order by p.createdAt desc
                    limit '''+offset+''','''+limit+''';'''
            
            record = (userId,)

            cursor = connection.cursor(dictionary=True)


            cursor.execute(query,record)

            resultList = cursor.fetchall()

            i = 0
            for row in resultList :
                resultList[i]['createdAt'] = row['createdAt'].isoformat()
                i = i + 1


            

        except Error as e :



            return{'error' : str(e)}, 500
        finally:
            cursor.close()
            connection.close()

        if len(resultList) == 0 :

            return {'error' : '잘못된 유저 아이디입니다.'}, 400

        return{'result' : 'success', 'items' : resultList,'count' : len(resultList)}

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

            

        except Error as e :
            
            print(e)
        
            
            return{"result" : 'fail','error' : str(e)}, 500
        finally:
            cursor.close()
            connection.close()

        return {"result" : "success"} , 200
    
# 유저 최종 포인트 적립
class TotalPointResource(Resource) :  
    @jwt_required()
    def get(self) :

        userId = get_jwt_identity()

        try :

            connection = get_connection()

            query = '''select userId, totalPoint , p.createdAt from points p
                    join user u
                    on p.userId = u.id
                    where u.id = %s
                    order by p.id desc limit 1;'''
            
            record = (userId,)

            cursor = connection.cursor(dictionary=True)


            cursor.execute(query,record)

            resultList = cursor.fetchall()

            i = 0
            for row in resultList :
                resultList[i]['createdAt'] = row['createdAt'].isoformat()
                i = i + 1


            

        except Error as e :
            return{'error' : str(e)}, 500
        finally:
            cursor.close()
            connection.close()

        if len(resultList) == 0 :

            return {'error' : '잘못된 유저 아이디입니다.'}, 400
        
        totalPoint = resultList[0]['totalPoint']

        return{'result' : 'success', 'totalPoint' : totalPoint}    
    
# 유저 쿠폰 추가
class CouponResource(Resource) :
    @jwt_required()
    def put(self, couponId) :
        userId = get_jwt_identity()

        try : 
            connection = get_connection()

            query = '''insert into yh_project_db.checkCoupon(userId, couponId)
                    values (%s, %s);'''

            record = (userId, couponId)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            

        except Error as e :
            
            print(e)
            
            
            return {"error" : str(e)}, 500
        finally:
            cursor.close()
            connection.close()

        return {"result" : "success"} , 200
    
    # 쿠폰 사용
    @jwt_required()
    def delete(self, couponId) :

        userId = get_jwt_identity()

        try : 
            connection = get_connection()
            
            query = '''delete from checkCoupon
                    where UserId= %s and couponId= %s;'''

            record = (userId,couponId)

            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()
            
        except Error as e:
            print(e)
            
            return {'error':str(e)},500
        
        finally:
            cursor.close()
            connection.close()

        return {'result':'success'},200
    
# 쿠폰조회
class CouponSearchResource(Resource) :
    @jwt_required()
    def get(self) :

        userId = get_jwt_identity()
        offset = request.args.get('offset')
        limit = request.args.get('limit')


        try : 
            connection = get_connection()
            
            query = '''select userId,couponId,title,description,discount,dateOfUseStart,dateOfUseEnd from coupons c
                    join checkCoupon k
                    on c.id = k.couponId
                    where userId = %s
                    limit ''' + offset + ''' , ''' + limit + ''' ; '''

            record = (userId,)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query , record)
            
            resultList = cursor.fetchall()

            i = 0
            for row in resultList :
                resultList[i]['dateOfUseStart'] = row['dateOfUseStart'].isoformat()
                resultList[i]['dateOfUseEnd'] = row['dateOfUseEnd'].isoformat()
                i = i + 1

     
            

        except Error as e :
            
            print(e)
            
            
            return{'error' : str(e)}, 500
        finally:
            cursor.close()
            connection.close()
        
        
        return{'result' : 'success' , 'couponList' : resultList, 'count' : len(resultList)}      


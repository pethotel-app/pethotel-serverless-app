from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

class HotelSearchResource(Resource):
    # 검색한 호텔 리스트 가져오기
    @jwt_required()
    def get(self):
        keyword = request.args.get('keyword')
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            # 검색 결과 개수를 구하는 쿼리 추가
            count_query = '''SELECT COUNT(*) as total_count
                             FROM yh_project_db.hotel
                             WHERE title LIKE %s OR addr LIKE %s'''
            count_params = ('%' + keyword + '%', '%' + keyword + '%')
            cursor = connection.cursor(dictionary=True)
            cursor.execute(count_query, count_params)
            total_count = cursor.fetchone()['total_count']

            # 검색 결과 목록을 가져오는 쿼리
            query = '''SELECT h.id, h.title, h.imgUrl, IFNULL(AVG(r.rating),0) AS avg, IFNULL(COUNT(r.hotelId),0) AS cnt,
                       IF(f.userId IS NULL, 0, 1) AS 'favorite'
                       FROM yh_project_db.hotel h
                       LEFT JOIN yh_project_db.follows f ON f.hotelId = h.id AND f.userId= %s
                       LEFT JOIN yh_project_db.reviews r ON r.hotelId = h.id
                       WHERE h.title LIKE %s OR h.addr LIKE %s
                       GROUP BY h.id
                       LIMIT %s, %s;'''
            params = (user_id, '%' + keyword + '%', '%' + keyword + '%', int(offset), int(limit))
            cursor.execute(query, params)
            result_list = cursor.fetchall()

            # 평균 평점을 실수형으로 변환
            for row in result_list:
                row['avg'] = float(row['avg'])

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success", "items": result_list, "count": total_count}, 200

    
     # 검색어 저장
    def put(self) :
        keyword = request.args.get('keyword')

        try :
            connection = get_connection()

            query = '''insert into yh_project_db.keyword(keyword)
                    values(%s);'''

            record = (keyword, )

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"result" : "fail", "error" : str(e)}, 500

        return {"result" : "success"}, 200
    
# 호텔 상세정보
class HotelInfoResource(Resource) :
    @jwt_required(optional=True)
    def get(self, hotelId) :


        try :
            connection = get_connection()

            query = '''select h.id,title,addr,longtitude,latitude,tel,imgUrl,naverUrl,description, small,medium,large
                    from hotel h
                    left join price p
                    on h.id = p.hotelId
                    where h.id = %s;'''


            record = (hotelId,)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query,record)

            resultList = cursor.fetchall()
            
            if resultList[0]['id'] is None :
                return{'error' : '잘못된 호텔 아이디 입니다.'} , 400

            i = 0
            for row in resultList :
                resultList[i]['longtitude'] = float(row['longtitude'])
                resultList[i]['latitude'] = float(row['latitude'])
                i = i + 1


            cursor.close()
            connection.close()



        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {'error' : str(e) } , 500

            


        return {'result' : 'success' , 'hotel' : resultList[0]}
    
    
class HotelSearchRankResource(Resource) :
    # 검색어 순위 가져오기
    def get(self) :
        today = request.args.get('today')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select keyword, ifnull(count(keyword),0) as cnt, createdAt
                    from (select * from yh_project_db.keyword where createdAt like '%''' + today + '''%' order by createdAt desc LIMIT 18446744073709551615) as `rank`
                    group by keyword
                    order by cnt desc
                    limit ''' + offset + ''' , ''' + limit + ''' ; '''

            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, )

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success", "items" : result_list, "count" : len(result_list)}, 200
    


# 무게별 가격
class HotelPriceResource(Resource) :
    @jwt_required(optional=True)
    def get(self,hotelId) :

        userId = get_jwt_identity()

        try :

            connection = get_connection()

            query = '''select * from price 
                     where hotelId = %s;'''
            
            record = (hotelId,)

            cursor = connection.cursor(dictionary=True)


            cursor.execute(query,record)

            resultList = cursor.fetchall()


            cursor.close()
            connection.close()

        except Error as e :


            cursor.close()
            connection.close()

            return{'error' : str(e)}, 500

        if len(resultList) == 0 :

            return {'error' : '잘못된 호텔 아이디입니다.'}, 400

        return{'result' : 'success', 'items' : resultList}


# 내 위치 주변 호텔
class HotelNearResource(Resource) :

    @jwt_required()
    def get(self) :


        long = request.args.get('long')
        lat = request.args.get('lat')
        limit = request.args.get('limit')
        offset = request.args.get('offset')
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select h.id, h.title, h.addr,if(h.description is null,"설명 등록 대기중입니다.",h.description) as description,h.imgUrl, ifnull(avg(r.rating),0) as avg, ifnull(count(r.hotelId),0) as cnt, h.longtitude, h.latitude,
                    if(f.userId is null, 0, 1) as 'favorite'
                    from yh_project_db.hotel h
                    left join yh_project_db.follows f on f.hotelId = h.id and f.userId= %s
                    left join yh_project_db.reviews r on r.hotelId = h.id
                    group by h.id
	                ORDER BY ((h.latitude - '''+lat+''') * (h.latitude - '''+lat+''') + (h.longtitude - '''+long+''') * (h.longtitude - '''+long+''')) ASC
                    limit ''' + offset + ''' , ''' + limit + ''' ; '''
            
            record = (user_id, )
            
            cursor = connection.cursor(dictionary=True)

            cursor.execute(query,record)

            result_list=cursor.fetchall()

            print(result_list)

            if result_list[0]['id'] is None :
                return{'error' : '잘못된 호텔 아이디 입니다.'} , 400

            i = 0
            for row in result_list :
                result_list[i]['avg'] = float(row['avg'])
                result_list[i]['longtitude'] = float(row['longtitude'])
                result_list[i]['latitude'] = float(row['latitude'])
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{"result":"fail","error":str(e)}, 500
        
        return {"result" : 'success','items':result_list,'count':len(result_list)}, 200


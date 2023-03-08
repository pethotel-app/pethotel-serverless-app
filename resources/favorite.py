from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

class FavoriteResource(Resource) :
    # 찜 추가
    @jwt_required()
    def post(self, hotelId) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into follows
                    (userId, hotelId)
                    values
                    (%s, %s);'''

            record = (user_id, hotelId)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success"}, 200

    # 찜 삭제
    @jwt_required()
    def delete(self, hotelId) :
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''delete from follows
                    where userId= %s and hotelId= %s;'''

            record = (user_id, hotelId)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success"}, 200

class FavoriteListResource(Resource) :
    # 내 찜목록 가져오기
    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select f.hotelId, h.title, h.imgUrl, ifnull(avg(r.rating),0) as avg, ifnull(count(r.hotelId),0) as cnt
                    from yh_project_db.follows f
                    left join yh_project_db.hotel h on f.hotelId = h.id
                    left join yh_project_db.reviews r on r.hotelId = h.id
                    where f.userId = %s
                    group by h.id
                    limit ''' + offset + ''' , ''' + limit + ''' ; '''

            record = (user_id, )

            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['avg'] = float(row['avg'])
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success", "items" : result_list, "count" : len(result_list)}, 200
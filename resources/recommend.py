from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
import pandas as pd
from mysql_connection import get_connection
from mysql.connector import Error

class HotelRecommendRealTimeResource(Resource) :

    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        # 추천할 갯수 가져오기
        count = request.args.get('count')
        count = int(count)

        try :
            connection = get_connection()

            # 전체 호텔 별점 가져와서 상관계수 구하기
            query = '''select h.id, h.title, r.userId, r.rating
                    from hotel h
                    left join reviews r on h.id = r.hotelId;'''

            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, )

            result_list = cursor.fetchall()

            df = pd.DataFrame(data= result_list)
            df = df.pivot_table(index='userId', columns='id', values='rating')
            hotel_correlations = df.corr(min_periods=3)

            # 내 별점 정보를 가져와야 내 맞춤형 추천 가능
            query = '''select h.id, h.title, r.rating
                    from reviews r
                    join hotel h on h.id = r.hotelId
                    where r.userId = %s;'''

            record = (user_id, )

            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        # 4. DB로부터 가져온 내 별점 정보를 데이터프레임으로 만든다
        myRating = pd.DataFrame(data= result_list)

        # 5. 내 별점 정보 기반으로 추천호텔 목록을 만든다
        similar_hotels_list = pd.DataFrame()

        for i in range( myRating.shape[0] ) :
            hotelTitle = myRating['id'][i]
            similar_hotel = hotel_correlations[hotelTitle].dropna().sort_values(ascending= False).to_frame()
            similar_hotel.columns = ['correlation']
            similar_hotel['weight'] = similar_hotel['correlation'] * myRating['rating'][i]
            similar_hotels_list = similar_hotels_list.append( similar_hotel )

        # 6. 중복 호텔은 제거한다(내가 리뷰 쓴 호텔 제거)
        drop_index_list = myRating['id'].to_list()

        for name in drop_index_list :
            if name in similar_hotels_list.index :
                similar_hotels_list.drop(name, axis=0, inplace= True)

        # 7. 중복 추천된 호텔은 weight가 가장 큰 값으로만 남기고 중복 제거한다
        recomm_hotel_list = similar_hotels_list.groupby('id')['weight'].max().sort_values(ascending= False).head(count)

        # 8. 제이슨(json)으로 클라이언트에게 보낸다
        recomm_hotel_list = recomm_hotel_list.to_frame().reset_index()
        recomm_hotel_list = recomm_hotel_list.to_dict('records')

        hotel_ids = [hotel['id'] for hotel in recomm_hotel_list]
        # print(hotel_ids) [284, 307, 299, 311, 326]

        try :
            connection = get_connection()

            query = '''select h.id, h.title, h.addr,
                    if(h.description is null, "설명 등록 대기중입니다.", h.description) as description,
                    h.imgUrl, ifnull(avg(r.rating),0) as avg, ifnull(count(r.hotelId),0) as cnt,
                    h.longtitude, h.latitude,
                    if(f.userId is null, 0, 1) as 'favorite'
                    from yh_project_db.hotel h
                    left join yh_project_db.reviews r on r.hotelId = h.id
                    left join yh_project_db.follows f on f.hotelId = h.id and f.userId= %s
                    where h.id in ({})
                    group by h.id;'''.format(','.join(str(i) for i in hotel_ids))
            
            record = (user_id, )
            
            cursor = connection.cursor(dictionary=True)

            cursor.execute(query,record)

            result_list=cursor.fetchall()

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

        # return {"result" : "success", "items" : recomm_hotel_list, "count" : len(recomm_hotel_list)}, 200

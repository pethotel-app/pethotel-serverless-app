
class Config :
    HOST = 'yh-104db.ce4cnusg3buq.ap-northeast-2.rds.amazonaws.com'
    DATABASE = 'yh_project_db'
    DB_USER = 'yh_project_db_user'
    DB_PASSWORD = 'yh1234db'

    SALT = 'asdghsjjjf543gfd'

    # JWT 관련 변수를 셋팅
    JWT_SECRET_KEY = 'yhacdemy20230105##hello'
    JWT_ACCESS_TOKEN_EXPIRES = False
    PROPAGATE_EXCEPTIONS = True

    # AWS 관련 키
    ACCESS_KEY = 'AKIAYG44LDKLA5XQ27GD'
    SECRET_ACCESS = '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'
    
    # S3 버킷
    S3_BUCKET = 'yunwltn-yh-test'
    # S3 Location
    S3_LOCATION = 'https://yunwltn-yh-test.s3.ap-northeast-2.amazonaws.com/'
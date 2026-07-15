from models.models import db,  Users, Role
from flask_security import SQLAlchemyUserDatastore
from redis import Redis

userdatastore = SQLAlchemyUserDatastore(db,Users,Role)




redis_client = Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)
from models.models import db, create_db, Users, Role
from flask_security import SQLAlchemyUserDatastore


userdatastore = SQLAlchemyUserDatastore(db,Users,Role)
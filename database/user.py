import tornado.gen
import bcrypt
from database import Document
from utils.threadpool import threadpool
from datetime import datetime as dt


class User(Document):
    """
    Document from db.users:
        _id    
        login
        email
        hashed_password
        access_level
        confirmed
        created   
    """
    
    table = Document.database.users
    onBeforeDelete = []
    
    ACCESS_ADMIN = 3
    ACCESS_MODER = 2
    ACCESS_USER = 1
    ACCESS_ANON = 0
    
    @classmethod
    def getSortedAccessNames(cls):
        return "anon", "user", "moder", "admin"
    
    @classmethod
    def getAccessNameLevel(cls, group):
        return getattr(cls, "ACCESS_" + group.upper())
        
    def check_access(self, access_level):
        return self["access_level"] >= access_level

    @tornado.gen.coroutine
    def update_password(self, new_password):
        self["hashed_password"] = hash_password(new_password)
        yield self.update()
        
    def check_password(self, password):
        return hash_check(password, self["hashed_password"])
        
    @classmethod
    @tornado.gen.coroutine
    def getByLoginOrEmail(cls, loginOrEmail, password):
        by_login = yield cls.find(login=loginOrEmail)
        by_email = yield cls.find(email=loginOrEmail)
        user = by_login or by_email
        if user and user.check_password(password):
            return user

    @classmethod
    @tornado.gen.coroutine
    def insert(cls, login, email, password, confirmed=False, access_level=None):
        doc = {
            "login": login,
            "email": email,
            "hashed_password": hash_password(password),
            "confirmed": confirmed,
            "access_level": cls.ACCESS_USER if access_level is None else access_level,
            "created": dt.now()}
        yield cls.table.insert_one(doc)
        return cls(doc)
        
    @property
    def is_admin(self):
        return self["access_level"] == self.ACCESS_ADMIN
        

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def hash_check(password, hash):
    return bcrypt.checkpw(password.encode(), hash)
from database import Document
from database.mail import Mail
from database.user import User
import tornado.gen
import utils, prj
from datetime import datetime as dt


class MailConfirm(Document):
    """
    Document from db.mailconfirms:
        _id
        type
        user_id
        back_url
        data
        created
    """
    
    table = Document.database.mailconfirms
    
    REGISTER = 'confirm-register'
    REGISTER_SUCCESS = 'confirm-register-success'
    MAILCHANGE = 'confirm-mailchange'
    MAILCHANGE_SUCCESS = 'confirm-mailchange-success'
    
    @classmethod
    @tornado.gen.coroutine
    def insert(cls, type, user, back_url=None, data=None):
        doc = {
            "_id": utils.random_token(),
            "type": type,
            "user_id": user["_id"],
            "back_url": back_url,
            "data": data,
            "created": dt.now()
        }
        yield cls.table.insert_one(doc)
        return cls(doc)
        

    @classmethod
    @tornado.gen.coroutine
    def insert_register(cls, handler, user):
        confirm = yield cls.insert(cls.REGISTER, user)
        confirm_url = prj.url + handler.reverse_url('mail-confirm', confirm['_id'])
        mail = yield Mail.insert(user['email'], cls.REGISTER, user, 
            # template arguments:
            confirm=confirm, 
            handler=handler, 
            confirm_url=confirm_url, 
            **prj.mailconfirm)
        
    @classmethod
    @tornado.gen.coroutine
    def insert_mailchange(cls, handler, user, email):
        confirm = yield cls.insert(cls.MAILCHANGE, user, data=email)
        confirm_url = prj.url + handler.reverse_url('mail-confirm', confirm['_id'])
        mail = yield Mail.insert(email, cls.MAILCHANGE, user, 
            # template arguments:
            confirm=confirm, 
            handler=handler, 
            confirm_url=confirm_url, 
            **prj.mailconfirm)
        
    @classmethod
    @tornado.gen.coroutine
    def onUserDelete(cls, user):
        yield cls.table.delete_many({"user_id": user["_id"]})
        
        
User.onBeforeDelete.append(MailConfirm.onUserDelete)
import tornado.gen 
from tornado.template import Template
from database import Document
from database.user import User
import prj
from datetime import datetime as dt


class Mail(Document):
    """
    Document from db.mails:
        _id
        user_id
        email
        subject
        html
        sent
        created
    """
    table = Document.database.mails
    
    @classmethod
    @tornado.gen.coroutine
    def insert(cls, email, type, user, **template_args):
        doc = {
            "user_id": user["_id"],
            "email": email,
            "subject": prj.mailer["subjects"][type].format(user=user, **template_args),
            "html": Template(open("templates/mail/%s.html" % type).read()).generate(user=user, **template_args),
            "sent": False,
            "created": dt.now(),
        }
        yield cls.table.insert_one(doc)
        return cls(doc)
        
    @classmethod
    @tornado.gen.coroutine
    def onUserDelete(cls, user):
        yield cls.table.delete_many({"user_id": user["_id"]})
        
        
User.onBeforeDelete.append(Mail.onUserDelete)
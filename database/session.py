from database import Document
from database.user import User
import tornado.gen
from datetime import datetime as dt
import utils


class Session(Document):
    """
    Document from db.sessions:
        _id
        user_id
        last_active
    """
    table = Document.database.sessions
    inactive_session_lifetime = 60 * 60 * 24  # seconds

    @classmethod
    @tornado.gen.coroutine
    def insert(cls, user):
        doc = {"user_id": user["_id"], "last_active": dt.now(), "_id": utils.random_token()}
        yield cls.table.insert_one(doc)
        return cls(doc)

    @classmethod
    @tornado.gen.coroutine
    def clear_expired(cls):
        yield cls.table.delete_many({"last_active": {"$lt": utils.dateback(cls.inactive_session_lifetime)}})

    @tornado.gen.coroutine
    def update_activity(self):
        self["last_active"] = dt.now()
        yield self.update()
        
    @classmethod
    @tornado.gen.coroutine
    def onUserDelete(cls, user):
        yield cls.table.delete_many({"user_id": user["_id"]})
        
        
User.onBeforeDelete.append(Session.onUserDelete)
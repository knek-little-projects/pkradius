import tornado.gen
import prj, utils
from datetime import datetime as dt
from bson.objectid import ObjectId


class MongoObject(dict):
    """
    Simple wrapper over MongoDB documents. 
    """
    
    def __eq__(self, other):
        return self["_id"] == other["_id"]
        

class Document(MongoObject):
    """
    Parent class for all MongoDB tables
    """
    
    database = prj.motor_database
    table = None

    @tornado.gen.coroutine
    def trigger(self, trigger_name):
        if hasattr(self, trigger_name):
            for func in getattr(self, trigger_name):
                yield func(self)

    @classmethod
    @tornado.gen.coroutine                
    def findMany(cls, **search):
        cursor = cls.table.find(search)
        result = []
        while (yield cursor.fetch_next):
            result.append(cursor.next_object())
        return result

    @classmethod
    @tornado.gen.coroutine
    def insert(cls, **doc):
        yield cls.table.insert_one(doc)
        return cls(doc)
        
    @tornado.gen.coroutine
    def remove(self):
        yield self.trigger("onBeforeDelete")
        yield self.table.delete_one({"_id": self["_id"]})
            
    @classmethod
    @tornado.gen.coroutine
    def find(cls, **search):
        doc = yield cls.table.find_one(search)
        if doc:
            return cls(doc)
            
    @classmethod
    @tornado.gen.coroutine
    def findByObjectId(cls, _id):
        return (yield cls.find(_id=ObjectId(_id)))
        
    @tornado.gen.coroutine
    def update(self):
        yield self.table.update_one({"_id": self["_id"]}, {"$set": utils.dict_exclude(self, "_id")})
           
    @classmethod
    @tornado.gen.coroutine
    def list(cls, limit_from, limit_to, sort_field, sort_direction, search):
        length = limit_to - limit_from
        cursor = cls.table.find(search)
        cursor = cursor.sort(sort_field, sort_direction)
        cursor = cursor.skip(limit_from).limit(length)
        docs = yield cursor.to_list(length)
        objs = [cls(doc) for doc in docs]
        return objs
        
    @classmethod
    @tornado.gen.coroutine
    def count(cls, **search):
        return (yield cls.table.count(search))
        
        
class Aggregator(MongoObject):
    """
    Parent class for all Mongo aggregators
    """
    
    database = prj.motor_database
    table = None
    pipeline = []
    
    @classmethod
    @tornado.gen.coroutine
    def aggregate(cls, *pipeline):
        cursor = yield cls.table.aggregate(list(cls.pipeline) + list(pipeline), cursor=False)
        return list(cursor)
    
    @classmethod
    @tornado.gen.coroutine
    def list(cls, limit_from, limit_to, sort_field, sort_direction, search):
        length = limit_to - limit_from
        pipe_sort = {"$sort": {sort_field: sort_direction}}
        pipe_skip = {"$skip": limit_from}
        pipe_limit = {"$limit": length} 
        pipe_match = {"$match": search}
        result = yield cls.aggregate(pipe_sort, pipe_match, pipe_skip, pipe_limit)
        return result

    @classmethod
    @tornado.gen.coroutine                
    def findMany(cls, **search):
        pipe_search = {"$match": search}
        result = yield cls.aggregate(pipe_search)
        return result
        
    @classmethod
    @tornado.gen.coroutine
    def count(cls, **search):
        pipe_search = {"$match": search}
        pipe_count = {"$group": {"_id": None, "count": {"$sum": 1}}}
        result = yield cls.aggregate(pipe_search, pipe_count)
        if result:
            return result[0]['count']
        else:
            return 0

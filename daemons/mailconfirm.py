import prj, logging, time, utils, threading
from prj import pymongo_database as db


class MailConfirmer(threading.Thread):
    """
    Thread to delete expired and not confirmed in time users
    """

    def run(self):

        while True:
        
            dead = {"created": {"$lt": utils.dateback(prj.mailconfirm["lifetime"])}}
            db.mailconfirms.delete_many(dead)
      
            dead["confirmed"] = False
            db.users.delete_many(dead)
      
            time.sleep(prj.mailconfirm["timeout"])

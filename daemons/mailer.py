import prj, time, traceback, logging, smtplib, threading
from prj import pymongo_database as db
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer(threading.Thread):
    """
    Thread to send emails from db.mails queue
    """
        
    def run(self):
        smtp = None
        
        while True:
            for mail in db.mails.find({"sent": False}).limit(prj.mailer["nbulk"]):
                logging.debug("{count} letters in queue".format(
                    subject=mail["subject"], 
                    count=db.mails.find({"sent": False}).count()))
                
                msg = self._prepare_message(mail)
                sent = False
                while not sent:
                    try:
                        if smtp is None:
                            smtp = self._new_smtp_connection()
                            assert smtp is not None 
                        smtp.send_message(msg)
                        db.mails.update_one(
                            {"_id": mail["_id"]}, 
                            {"$set": {"sent": True}})
                        sent = True
                    except Exception as e:
                        logging.debug("Error on send — %s" % str(e))
                        traceback.print_exc()
                        smtp = self._new_smtp_connection()
                        time.sleep(prj.mailer["timeout"])

            logging.debug("0 letters in queue... sleeping")
            time.sleep(prj.mailer["timeout"])

    def _new_smtp_connection(self):
        try:
            smtp = smtplib.SMTP(prj.mailer["server"], prj.mailer["port"])
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(prj.mailer["login"], prj.mailer["password"])
        except Exception as e:
            logging.error("Connection error — %s" % str(e))
            smtp = None
        return smtp
    
    def _prepare_message(self, mail):
        msg = MIMEMultipart("alternative")
        msg.set_charset("utf-8")
        msg["Subject"] = mail["subject"]
        msg["From"] = self._from
        msg["To"] = mail['email']
        html = MIMEText(mail["html"].decode(), "html")
        msg.attach(html)
        return msg
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._from = '{title} <{email}>'.format(**prj.mailer)
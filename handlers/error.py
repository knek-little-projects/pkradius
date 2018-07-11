from handlers.user import UserHandler
import tornado.gen


class ErrorHandler(UserHandler):

    def __init__(self, *args, code=500, **kwargs):
        self.code = code
        super().__init__(*args, **kwargs)
        
    def get(self):
        self.render("error.html", status_code=self.code, reason=None, kwargs=None)

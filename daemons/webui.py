#!/usr/bin/python3
import database, os, threading
import prj, prj.handlers
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop        


class Application(tornado.web.Application):

    def __init__(self):
        super().__init__(
            login_url = prj.handlers.login_url, 
            handlers = prj.handlers.handlers,
            ui_modules = prj.handlers.ui_modules,
            template_path = os.path.join(os.getcwd(), "templates"),
            static_path = os.path.join(os.getcwd(), "static"),
            cookie_secret = prj.app["cookie_secret"],
            debug = True,
            xsrf_cookies = True,
            **prj.handlers.default_handler
        )


class WebUI(threading.Thread):

    def __init__(self, port):
        super().__init__()
        self._port = port
        
    def run(self):
        HTTPServer(Application()).listen(self._port)
        IOLoop.instance().start()    
    
    
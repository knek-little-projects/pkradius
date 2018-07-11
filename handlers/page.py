from handlers.user import UserHandler, authorized_level
from database.user import User
import tornado.web
import tornado.gen


class PageHandler(UserHandler):
    
    def initialize(self, template, access_level, template_params):
        self.template = template
        self.access_level = access_level
        self.template_params = template_params
        
    @authorized_level
    @tornado.gen.coroutine
    def get(self):
        self.render(self.template, **self.template_params)
    

def page(name, urlname=None, addr=None, template=None, access_level=None, **kwargs):
    """
    Generate tornado.web.url for PageHandler
    """

    if addr is None:
        addr = "/" + name

    if template is None:
        template = "page/%s.html" % name

    if urlname is None:
        urlname = "page-" + name
        
    if access_level is None:
        access_level = User.ACCESS_USER

    return tornado.web.url(
        addr, 
        PageHandler, 
        name=urlname, 
        kwargs=dict(
            template=template,
            template_params=kwargs,
            access_level=access_level))

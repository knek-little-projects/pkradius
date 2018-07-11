import prj, json, utils, urllib
import tornado.web
import tornado.gen


class RequestHandler(tornado.web.RequestHandler):
    """
    Parent class for all HTTP Handlers
    """
    
    def get_template_namespace(self):
        """
        Extend template namespace with
        - `prj` module
        - `app` shortcut
        """
        template_namespace = super().get_template_namespace()
        template_namespace["app"] = self.application
        template_namespace["prj"] = prj
        return template_namespace

    def reverse_url(self, url, *args, **kwargs):
        """
        Add params to reverse_url
        """
        url = super().reverse_url(url, *args)
        if len(kwargs) > 0:
            url += '?' + urllib.parse.urlencode(kwargs)
        return url

    def redirect(self, relative_url):
        """
        Allow only relative urls 
        """
        base_url = self.request.protocol + "://" + self.request.host
        if relative_url and relative_url[0] == "/":
            super().redirect(base_url + relative_url) # normal behaviour
        else:
            super().redirect("/") # phishing detected

    def reverse_redirect(self, *args, **kwargs):
        super().redirect(self.reverse_url(*args, **kwargs))

    def login_redirect(self):
        super().redirect(self.get_login_url() + "?" + urllib.parse.urlencode({"next": self.request.uri}))
        
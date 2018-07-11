import tornado.web
import tornado.gen 
import tornado.web
import urllib
import math, json, re


class UIModule(tornado.web.UIModule):
    """
    Parent class for all UI Modules
    """
    pass
    

class DocumentUI(tornado.web.UIModule):

    def render(self, doc, fields, child=False):
        rows = []
        for field in fields:
            rows.append((field, doc[field]))
            
        if child:
            table_class = "general doc child"
        else:
            table_class = "general doc"
            
        return self.render_string("ui/document.html", fields=fields, rows=rows, table_class=table_class)
        

class PagerUI(tornado.web.UIModule):

    def render(self, pager):
        return self.render_string("ui/pager.html", 
            show=pager.show,
            page=pager.page,
            page_count=pager.page_count)

from handlers.user import UserHandler, authorized_admin, authorized_level
from database.user import User
import tornado.gen
import json, datetime
from utils.pager import DocumentPager
from importlib import import_module


class TableHandler(UserHandler):
    """
    HTTP handler for table of database.Document objects
    """
    
    def initialize(self, 
            template, 
            data_source, 
            access_level=User.ACCESS_USER, 
            template_params={}, 
            pager_params={}):
        """
        :param data_source: database.Document child
        :param access_level: User.access_level
        :param pager_params: utils.Pager params
        :param template: address of template file...
        :param template_params: ...and its params
        """
        self.template = template
        self.access_level = access_level
        self.data_source = data_source
        self.template_params = template_params
        self.pager_params = pager_params
        
    @authorized_level
    @tornado.gen.coroutine
    def get(self):
        elements = DocumentPager(handler=self, **self.pager_params)
        yield elements.fetch(self.data_source)
        self.render(
            self.template,
            elements=elements,
            **self.template_params)
            
# TODO:
#         if self.download_params and self.get_argument("download", False):
#             yield self.get_csv()
#         else:
#     @tornado.gen.coroutine
#     def get_csv(self):
#         attachment_header = "attachment; filename={filename}-{datetime:%Y-%m-%d}.csv".format( 
#             filename=self.download_params["file_name"], 
#             datetime=datetime.datetime.now())
#         csv_headers = ';'.join(self.download_params['headers']) + "\r\n"
#             
#         self.set_header("Content-Type", "application/force-download")
#         self.set_header("Content-Disposition", attachment_header)
#         self.write(csv_headers)
#         
#         yield db.map_many(
#             table, 
#             lambda d: data.append(';'.join(self.download['map_func'](d))),
#             *self.download['sort'], 
#             **self.download['search'])
#         data = []
#         yield self.table.map_many(
#             )
#         self.write('\r\n'.join(data))


def table(name, restrict_search=None, **kwargs):
    """
    Generate tornado.web.url for TableHandler
    """

    words = name.split('-')
    addr = '/' + '/'.join(words)
    
    if "template" not in kwargs:
        kwargs["template"] = words[0] + '/' + '-'.join(words[1:]) + '.html'
    
    if "data_source" not in kwargs:
        kwargs["data_source"] = getattr(import_module("database." + words[0]), words[0].title())
    
    if "pager_params" not in kwargs:
        kwargs["pager_params"] = {}
    
    kwargs["pager_params"]["restrict_search"] = restrict_search

    return tornado.web.url(
        addr, 
        TableHandler, 
        name=name, 
        kwargs=kwargs)
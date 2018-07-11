import tornado.gen
import math, re, json


class Pager:
    """
    Base class for specific data source pagers.
    """

    def __init__(self, handler, page=0, show=50,
                 select={}, restrict_search=None, sort="_id", direction=1, show_max=100000, regex=False):
        """
        Extract pager params from :param handler: and prepare page of documents.
    
        :param handler: tornado RequestHandler
        :param restrict_search: allow user to search only those fields (default is None = allow all)
        :param show: number of elements per page
        :param select: initial MongoDB search query
        :param regex: allow regex in user searches
        
        Pager extract GET arguments from http handler:
        - search (complement :param select: value, but not replaces it)
        - show (replaces :param show: value)
        - page (replaces :param page: value)
        - sort (replaces :param sort: value)
        - direction (replaces :param direction: value)
        """        
        self.page = int(handler.get_argument("page", page))
        self.show = min(show_max, int(handler.get_argument("show", show)))
        self.sort = str(handler.get_argument("sort", sort))
        self.direction = int(handler.get_argument("direction", direction))
        
        # prepare search
        search_string = handler.get_argument("search", "{}")
        self.search = {}
        user_search = json.loads(search_string)
        for key in user_search:
            if restrict_search is None or key in restrict_search:
                value = str(user_search[key])
                if regex:
                    try:
                        value = re.compile(value, re.IGNORECASE)
                    except:
                        value = re.compile(re.escape(value), re.IGNORECASE)
                else:
                    value = re.compile(re.escape(value), re.IGNORECASE)
                self.search[key] = value
                
        for key in select:
            self.search[key] = select[key]

    def fetch(self, data_source):
        """
        This method should prepare the following object properties:
        - self.doc_count -- overall number of documents for `search`
        - self.page_count -- overall number of pages for `search` and `show`
        - self.docs -- list of documents on the `page` for `search`, `show`, `sort` and `direction`
        """
        pass

    def __iter__(self):
        for doc in self.docs:
            yield doc


class DocumentPager(Pager):
    """
    Paginate database.Document objects stored in MongoDB
    """

    @tornado.gen.coroutine
    def fetch(self, DocumentObject):
        """
        :param DocumentObject: database.Document child
        """
        self.doc_count = yield DocumentObject.count(**self.search)
        self.page_count = math.ceil(self.doc_count / self.show)
        self.docs = yield DocumentObject.list(self.page * self.show, (self.page + 1) * self.show, self.sort, self.direction, self.search)




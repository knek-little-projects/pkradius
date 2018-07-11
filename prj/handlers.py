"""
    Project HTTP handlers and UI modules.
"""
from tornado.web import url, StaticFileHandler
from handlers.page import page
from handlers.table import table
from handlers.error import ErrorHandler
from handlers.ui import PagerUI, DocumentUI
from handlers.user import *
import functools


page = functools.partial(page, access_level=0)


login_url = r"/user/login"
handlers = [
    # user profile
    url(login_url, UserLogin, name="user-login"),
    url(r"/user/register", UserRegister, name="user-register"),
    url(r"/user/logout", UserLogout, name="user-logout"),
    url(r"/user/view/(.*)", UserView, name="user-view"),
    url(r"/user/edit/remove/(.*)", UserEditRemove, name="user-edit-remove"),
    url(r"/user/edit/general/(.*)", UserEditGeneral, name="user-edit-general"),
    url(r"/user/edit/password/(.*)", UserEditPassword, name="user-edit-password"),
    url(r"/user/confirm-info/(.*)/(.*)", MailConfirmInfo, name="confirm-info"),
    url(r"/user/confirm/(.*)", MailConfirmHandler, name="mail-confirm"),
    table("user-list", restrict_search=["login"]),

    # static files
    url(r"/(favicon.ico|robots.txt)", StaticFileHandler, kwargs=dict(path="static")),

    # simple pages
    page("main", addr="/"),
    
    page("gibka-aljuminievyh-okonnyh-i-dvernyh-profilej", 
        template="page/slider.html", 
        title="Гибка алюминиевых оконных и дверных профилей"),
        
    page("gibka-aljuminievyh-fasadnyh-profilej-dlja-ploskogo-osteklenija-po-H", 
        template="page/slider.html",
        title="Гибка алюминиевых фасадных профилей для плоского остекления (по Х)"),
        
    page("gibka-aljuminievyh-fasadnyh-profilej-dlja-molirovanogo-osteklenija-po-Y", 
        template="page/slider.html",
        title="Гибка алюминиевых фасадных профилей для молированого остекления (по Y)"),
        
    page("dvuhploskostnaja-gibka-aljuminievyh-fasadnyh-profilej-po-X-i-Y", 
        template="page/slider.html",
        title="Двухплоскостная гибка алюминиевых фасадных профилей (по X и Y)"),
        
    page("gibka-aljuminievyh-fasadnyh-profilej-dlja-arok-na-radiusnyh-stenah-X-Y-Z", 
        template="page/slider.html",
        title="Гибка алюминиевых фасадных профилей для арок на радиусных стенах (X, Y, Z)"),
        
    page("gibka-profilej-dlja-peregorodok-i-dlja-peril", 
        template="page/slider.html",
        title="Гибка профилей для перегородок и для перил"),
        
    page("gibka-stalnyh-profilej", 
        template="page/slider.html",
        title="Гибка стальных профилей"),
        
    page("gibka-aljuminievyh-profilej-obshhestroitelnogo-naznachenija", 
        template="page/slider.html",
        title="Гибка алюминиевых профилей общестроительного назначения"),
    
    page("about"),
    page("tech"),
    page("calc"),
    page("gallery"),
    page("form", template="page/uc.html"),
    page("contact"),
    page("partners"),
]


ui_modules = {
    "Pager": PagerUI,
    "Document": DocumentUI
}


default_handler = {
    "default_handler_class": ErrorHandler,
    "default_handler_args": dict(code=404)
}
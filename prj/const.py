"""
    Application constants:
    - app title
    - database settings
    - mailer settings
    etc.
    
    All this settings are available in tornado templates via `prj` variable. 
"""
import socket


app = {
    "title": "ПК Радиус",
    "database_name": "pkradius",
    "cookie_secret": "",
    "verbosity": "warn", # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "url": "http://pkradius.ru" if "token-economy" in socket.gethostname() else "http://localhost:12345",
    "session_cookie_lifetime": 30  # days
}


mailer = {
    "title": "ПК Радиус",
    "login": "pkradius",
    "email": "pkradius@yandex.ru",
    "password": "",
    "server": "smtp.yandex.ru",
    "port": 587,
    "nbulk": 100,
    "timeout": 5,
    "subjects": {
        "confirm-register": "Подтверждение регистрации",
        "confirm-mailchange": "Подтверждение изменения email"
    }
}


mailconfirm = {
    "confirm_description": "Ссылка действительна в течение часа и лишь при первом переходе.",
    "timeout": 900,
    "lifetime": 3600
}


scripts = [
    "jquery-3.1.1.min.js", 
    "general.js", 
    "html.js", 
    "location.js", 
    "transform.js", 
    "pager.js", 
    "table.js",
    "slick.min.js"
]


stylesheets = [
    "content-table.css", 
    "form.general.css", 
    "main-content.css", 
    "main-menu.css", 
    "pager.css", 
    "table.general.css", 
    "tabs.css",
    "layout.css", 
    "main-logo.css", 
    "general.css",
    "slick.css",
    "slick-theme.css",
    "pkradius.css"
]


def get_cv(path="static/img/cv/"):

    import os
    import re
    
    re_image = re.compile("\.(jpe?g|png|giff?)$", flags=re.I)
    
    cv = {}
    for dirname in os.listdir(path):
        if dirname not in cv:
            cv[dirname] = []
        cv_dir = cv[dirname]
        
        for filename in os.listdir(os.path.join(path, dirname)):
            if re_image.search(filename):
                cv_dir.append({
                    "path": os.path.join(path, dirname, filename),
                    "title": filename[:filename.rfind(".")]
                })
    
    return cv
            
cv = get_cv()
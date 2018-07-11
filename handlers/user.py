from handlers import RequestHandler
from database.session import Session
from database.user import User
from database.mailconfirm import MailConfirm
import tornado.web
import tornado.gen 
import tornado.escape
import json, datetime, utils, prj


SESSION_INACTIVE_LIFETIME = 60 * 60 * 24
SESSION_EXPIRES_DAYS = 30


def authorized_admin(f):
    """
    Decorator: allow access to the handler only to admin
    """
    @tornado.gen.coroutine
    def check_access(handler, *args, **kwargs):
        if handler.current_user:
            if handler.current_user.is_admin:
                yield f(handler, *args, **kwargs)
            else:
                handler.write_error(403, reason="Access restricted")
        else:
            handler.login_redirect()
    return check_access
    
    
def authorized_level(f):
    """
    Decorator: check current_user access rights to the handler
    """
    @tornado.gen.coroutine
    def check_access(handler, *args, **kwargs):
        # handler allowed to anyone
        if handler.access_level == 0: 
            yield f(handler, *args, **kwargs)
            
        # handler allowed only to authenticated users
        elif handler.current_user: 
            if handler.current_user.check_access(handler.access_level):
                yield f(handler, *args, **kwargs)
            else: 
                handler.write_error(403, reason="Access restricted")
        else: 
            handler.login_redirect()
    return check_access
    

def user_exists(f):
    """
    Decorator: transform f(login, ...) -> f(user, ...)
    Warning: @user_exists does not imply @authenticated
    """
    @tornado.gen.coroutine
    def find_user(handler, login, *args, **kwargs):
        user = yield User.find(login=login)
        if user:
            return (yield f(handler, user, *args, **kwargs))
        else:
            handler.write_error(404, reason="User not found")
    return find_user


def authorized_edit(f):
    """
    Decorator:
    1) transform f(login, ...) -> f(user, ...)
    2) check current_user rights to edit user profile
    """
    @user_exists
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def check_access(handler, user, *args, **kwargs):
        if handler.current_user == user or handler.current_user.is_admin:
            return (yield f(handler, user, *args, **kwargs))
        else:
            handler.write_error(403, reason="You have no rights to edit this page")
    return check_access


class UserHandler(RequestHandler):
    """
    Parent class for all user handlers
    """
    
    @tornado.gen.coroutine
    def prepare(self):
        self.current_user = yield self.get_current_user()

    @tornado.gen.coroutine
    def get_current_user(self):
        session_id = self.get_cookie("session_id")
        self.current_session = yield Session.find(_id=session_id)
        if self.current_session:
            user = yield User.find(_id=self.current_session["user_id"])
            if user:
                yield self.current_session.update_activity()
                return user
                
    def write_error(self, status_code, reason=None, **kwargs):
        if not isinstance(self.current_user, User):
            # dirty hack for situation where .prepare() didn't start
            self.current_user = prj.pymongo_database.users.find_one({"_id": self.get_cookie("session_id")})
        super().render("error.html", status_code=status_code, reason=reason, kwargs=kwargs)

    @tornado.gen.coroutine
    def set_current_user(self, user):
        yield Session.clear_expired()
        self.current_session = yield Session.insert(user)
        self.set_cookie("session_id", self.current_session["_id"], httponly=True, path="/", expires_days=prj.app["session_cookie_lifetime"])
            

class UserLogin(UserHandler):
    
    @tornado.gen.coroutine
    def get(self, **flags):
        if self.current_user:
            self.redirect(self.get_argument("next", "/"))
        else:
            self.render("user/login.html", flags=flags)

    @tornado.gen.coroutine
    def post(self):
        login = self.get_argument("login")
        password = self.get_argument("password")
        next = self.get_argument("next", "/")
        
        user = yield User.getByLoginOrEmail(login, password)
        if user:
            if user["confirmed"]:
                yield self.set_current_user(user)
                self.redirect(next)
            else:
                self.reverse_redirect("confirm-info", user["login"], MailConfirm.REGISTER)
        else:
            self.get(wrong_credentials=True)


class UserLogout(UserHandler):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        yield self.current_session.remove()
        self.redirect("/")


class UserRegister(UserHandler):

    @authorized_admin
    @tornado.gen.coroutine
    def get(self, **flags):
        self.render("user/register.html", flags=flags)

    @authorized_admin
    @tornado.gen.coroutine
    def post(self):
        login = self.get_argument("login")
        email = self.get_argument("email")
        password = self.get_argument("password")
        password_repeat = self.get_argument("password_repeat")
        next = self.get_argument("next", "/")

        if password != password_repeat:
            yield self.get(password_repeat=True)
            
        elif "/" in login or "\\" in login:
            yield self.get(login_pattern=True)
            
        elif (yield User.find(login=login)):
            yield self.get(login_exists=True)
            
        elif (yield User.find(email=email)):
            yield self.get(email_exists=True)
            
        else:
            user = yield User.insert(login, email, password)
            confirm = yield MailConfirm.insert_register(user=user, handler=self)
            self.reverse_redirect("confirm-info", user["login"], MailConfirm.REGISTER)


class UserView(UserHandler):

    @user_exists
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, user):
        self.render("user/view.html", user=user)


class UserEdit(UserHandler):
    """
    Parent class for all user edit profile handlers
    """

    @authorized_edit
    @tornado.gen.coroutine
    def get(self, user):
        self.render(user)

    @authorized_edit
    @tornado.gen.coroutine
    def post(self, user):
        if self.current_user.is_admin:
            yield self.post_admin(user)
        else:
            yield self.post_user(user)

    @tornado.gen.coroutine
    def post_admin(self, user):
        yield self.post_user(user)

    @tornado.gen.coroutine
    def post_user(self, user):
        pass


class UserEditGeneral(UserEdit):

    def render(self, user, **flags):
        super().render("user/edit-general.html", user=user, flags=flags)

    @tornado.gen.coroutine
    def post_admin(self, user):
        login = self.get_argument("login")
        email = self.get_argument("email")
        access_level = int(self.get_argument("access_level"))
        
        if login != user["login"] and (yield User.find(login=login)):
            self.render(user, login_collision=True)
        
        elif email != user["email"] and (yield User.find(email=email)):
            self.render(user, email_collision=True)

        else:
            user["login"] = login
            user["email"] = email
            user["access_level"] = access_level
            yield user.update()
            self.reverse_redirect("user-view", user["login"])

    @tornado.gen.coroutine
    def post_user(self, user):
        login = self.get_argument("login")
        email = self.get_argument("email")
        password = self.get_argument("password")

        if user.check_password(password):

            if login != user["login"] and (yield User.find(login=login)):
                self.render(user, login_collision=True)
                
            elif email != user["email"] and (yield User.find(email=email)):
                self.render(user, email_collision=True)
                
            else:
                user["login"] = login
                yield user.update()
                
                if email != user["email"]:
                    yield MailConfirm.insert_mailchange(user=user, email=email, handler=self)                
                    self.reverse_redirect("confirm-info", user["login"], MailConfirm.MAILCHANGE)
                else:
                    self.reverse_redirect("user-view", user["login"])
        else:
            self.render(user, wrong_password=True)


class UserEditRemove(UserEdit):

    def render(self, user):
        super().render("user/remove.html", user=user)

    @tornado.gen.coroutine
    def post_admin(self, user):
        yield user.remove()
        self.reverse_redirect('user-list')


class UserEditPassword(UserEdit):

    def render(self, user, **flags):
        super().render("user/edit-password.html", user=user, flags=flags)

    @tornado.gen.coroutine
    def post_admin(self, user):
        new_password = self.get_argument("new_password")
        new_password_repeat = self.get_argument("new_password_repeat")
        
        if new_password != new_password_repeat:
            self.render(user, password_repeat=True)
        else:
            yield user.update_password(new_password)
            self.reverse_redirect("user-view", user["login"])

    @tornado.gen.coroutine
    def post_user(self, user):
        new_password = self.get_argument("new_password")
        new_password_repeat = self.get_argument("new_password_repeat")
        old_password = self.get_argument("old_password")
        
        if not user.check_password(old_password):
            self.render(user, wrong_password=True)
            
        elif new_password != new_password_repeat:
            self.render(user, password_repeat=True)
            
        else:
            yield user.update_password(new_password)
            self.reverse_redirect("user-view", user["login"])

    
class MailConfirmHandler(UserHandler):

    @tornado.gen.coroutine
    def get(self, key):
        confirm = yield MailConfirm.find(_id=key)
        if confirm:
            user = yield User.find(_id=confirm["user_id"])
            if user:
                if confirm["type"] == MailConfirm.REGISTER:
                    yield self.confirm_register(user, confirm)
                
                elif confirm["type"] == MailConfirm.MAILCHANGE:
                    yield self.confirm_mailchange(user, confirm)
            
                else:
                    self.write_error(500, "Unknown confirmation type (%s)" % confirm["type"])
            else:
                self.write_error(404, "User not found")
            yield confirm.remove()
        else:
            self.write_error(404, "Confirmation URL expired")

    @tornado.gen.coroutine
    def confirm_mailchange(self, user, confirm):
        user["email"] = confirm["data"]
        yield user.update()
        self.reverse_redirect("confirm-info", user["login"], MailConfirm.MAILCHANGE_SUCCESS)
    
    @tornado.gen.coroutine
    def confirm_register(self, user, confirm):
        user["confirmed"] = True
        yield user.update()
        yield self.set_current_user(user)
        self.reverse_redirect("confirm-info", user["login"], MailConfirm.REGISTER_SUCCESS)
            

class MailConfirmInfo(UserHandler):
    
    @user_exists
    @tornado.gen.coroutine
    def get(self, user, confirm_type):
        self.render("user/confirm-info.html", user=user, confirm_type=confirm_type)

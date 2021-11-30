from flask import request, redirect, url_for, current_app
from urllib.parse import urlparse, urljoin
from flask.helpers import flash, make_response
from flask_login import current_user

def is_safe_redirect_url(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return (
        redirect_url.scheme in ("http", "https")
        and host_url.netloc == redirect_url.netloc
    )


def get_safe_redirect(url):

    if url and is_safe_redirect_url(url):
        return url

    url = request.referrer
    if url and is_safe_redirect_url(url):
        return url
        
    return "/"

def admin_required(func):
    def admin_wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            if (request.accept_mimetypes.best == "application/json"):
                resp = make_response(dict(msg="login-redirect",location= url_for('auth.loginAdmin', next=request.url)))
                return resp
            else:
                return redirect(url_for('auth.loginAdmin', next=request.url))
        elif not current_user.admin:
                flash("You must log in as admin")
                return current_app.login_manager.unauthorized()
        else:
            return func(*args, **kwargs)
    admin_wrapper.__name__ = func.__name__
    return admin_wrapper

def student_required(func):
    def student_wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            if (request.accept_mimetypes.best == "application/json"):
                resp = make_response(dict(msg="login-redirect",location= url_for('auth.loginStudent', next=request.url)))
                return resp
            else:
                return redirect(url_for('auth.loginStudent', next=request.url))
        elif current_user.admin:
            flash("You must log in as student")
            return current_app.login_manager.unauthorized()
        else:
            return func(*args, **kwargs)
    student_wrapper.__name__ = func.__name__
    return student_wrapper
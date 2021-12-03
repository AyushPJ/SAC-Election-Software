from datetime import datetime
from flask import request, redirect, url_for, current_app
from urllib.parse import urlparse, urljoin
from flask.templating import render_template
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
            if request.accept_mimetypes.best == "application/json":
                return current_app.login_manager.unauthorized() 
            return redirect(url_for('auth.loginAdmin', next=request.url))
        elif not current_user.admin:
            return render_template("error.html",msg="Must login as admin to continue.", title="Unauthorized", statusCode="401"), 401
        else:
            return func(*args, **kwargs)
    admin_wrapper.__name__ = func.__name__
    return admin_wrapper

def student_required(func):
    def student_wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.accept_mimetypes.best == "application/json":
                return current_app.login_manager.unauthorized() 
            return redirect(url_for('auth.loginStudent', next=request.url))
        elif current_user.admin:
            return render_template("error.html",msg="Must login as student to continue.", title="Unauthorized", statusCode="401"), 401
        else:
            return func(*args, **kwargs)
    student_wrapper.__name__ = func.__name__
    return student_wrapper


def voting_required(func):
    def voting_wrapper(*args, **kwargs):
        voteStatus = current_app.config['VOTING']
        voterStatus = current_user.get_votingStatus();
        if not voteStatus['status']:
            return render_template("error.html",msg="Voting is now closed.", title="Not Allowed", statusCode="401"), 401
        elif voteStatus['status'] == "Automatic":
            currentDT = datetime.utcnow()
            if((voteStatus['open'] and voteStatus['open'] <= currentDT) or not voteStatus['open']):
                if ((voteStatus['close'] and currentDT <= voteStatus['close']) or not voteStatus['close']):
                    if not voterStatus:
                        return func(*args, **kwargs)

                    else:
                        if (request.accept_mimetypes.best == "application/json"):
                            return render_template("error.html",msg="You are allowed to vote only once.", title="Not Allowed", statusCode="401"), 401
                        else:
                            return render_template('vote-successful.html')
            
            return render_template("error.html",msg="Voting is now closed.", title="Not Allowed", statusCode="401"), 401
        elif voteStatus['status']:
            if not voterStatus:
                return func(*args, **kwargs)
            else:
                if (request.accept_mimetypes.best == "application/json"):
                    return render_template("error.html",msg="You are allowed to vote only once.", title="Not Allowed", statusCode="401"), 401
                else:
                    return render_template('vote-successful.html')

    voting_wrapper.__name__ = func.__name__
    return voting_wrapper

def application_required(func):
    def application_wrapper(*args, **kwargs):
        appStatus = current_app.config['APPLICATIONS']
        if not appStatus['status']:
            return render_template("error.html",msg="Applications are now closed.", title="Not Allowed", statusCode="401"), 401
        elif appStatus['status'] == "Automatic":
            currentDT = datetime.utcnow()
            if((appStatus['open'] and appStatus['open'] <= currentDT) or not appStatus['open']):
                if ((appStatus['close'] and currentDT <= appStatus['close']) or not appStatus['close']):
                    return func(*args, **kwargs)
            else:
                return render_template("error.html",msg="Applications are now closed.", title="Not Allowed", statusCode="401"), 401
        elif appStatus['status']:
            return func(*args, **kwargs)
    application_wrapper.__name__ = func.__name__
    return application_wrapper
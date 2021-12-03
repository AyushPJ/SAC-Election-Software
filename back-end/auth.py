import re
from flask import Blueprint, current_app, flash, jsonify
from flask import request, render_template, redirect, url_for

from flask_login import login_user, logout_user, login_required, current_user
from google.oauth2 import id_token
from google.auth.transport import requests
from werkzeug.exceptions import NotFound

bp = Blueprint("auth", "auth", url_prefix="/auth")

@bp.route("/login/student", methods=["GET"])
def loginStudent():
    next = ''
    if 'next' in request.args:
        next = request.args.get('next')

    return render_template('student_login.html',next=next)

@bp.route("/login/admin", methods=["GET"])
def loginAdmin():
    next = ''
    if 'next' in request.args:
        next = request.args.get('next')
    return render_template('admin_login.html',next=next)

@bp.route("/login/callback", methods=["POST"])
def loginCallback():

    csrf_token_cookie = request.cookies.get('g_csrf_token')
    if not csrf_token_cookie:
        return 'No CSRF token in Cookie.', 400
    csrf_token_body = request.form.get('g_csrf_token')
    if not csrf_token_body:
        return 'No CSRF token in post body.', 400
    if csrf_token_cookie != csrf_token_body:
        return 'Failed to verify double submit cookie.', 400

    token = request.form.get('credential')
    
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), current_app.config['GOOGLE_CLIENT_ID'])
        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        if idinfo['email_verified']:
            id_ = idinfo['sub']
            email = idinfo['email']
            profilePic = idinfo['picture']
            name = idinfo['name']

            
            from .user import User

            userClass=request.args.get('user-class')

            if not User.get(id_):
                if userClass == "student":
                    retCode = User.createStudent(id=id_, name=name, email=email, profilePic=profilePic)
                    if retCode == -1:
                        return render_template('error.html', msg="You are not a registered student.", statusCode="401", title="Not Allowed"), 401
                    elif retCode == -2:
                        return render_template('error.html', msg="You are not eligible to participate in the elections.", statusCode="401", title="Not Allowed"), 401
                elif userClass == "admin":
                    retCode = User.createAdmin(id=id_, name=name, email=email, profilePic=profilePic)
                    if retCode == -1:
                        return render_template('error.html', msg="You are not a registered admin.", statusCode="401", title="Not Allowed"), 401
                else:
                    return "Invalid request format", 400
            
            user = User.get(id_)

            if user.admin and userClass=="student":
                return render_template('error.html', msg="You are not a registered student.", statusCode="401", title="Not Allowed"), 401
            elif not user.admin and userClass=="admin":
                return render_template('error.html', msg="You are not a registered admin.", statusCode="401", title="Not Allowed"), 401

            # Send user back to homepage
            login_user(user)
            if 'next' not in request.args:
                if user.admin:
                    next_url = url_for('admin.index')
                else:
                    next_url = url_for('student.index')
            else:
                if request.args.get('next') == '':
                    if user.admin:
                        next_url = url_for('admin.index')
                    else:
                        next_url = url_for('student.index')
                else:
                    from .utils import get_safe_redirect
                    next_url = get_safe_redirect(request.args.get('next'))
            return redirect(next_url)

        else:
            return render_template('error.html', msg="Account not verified by Google.", statusCode="400", title="Bad Request"), 400

    except ValueError:
        return render_template('error.html', msg="Invalid token.", statusCode="400", title="Bad Request"), 400


@bp.route("/logout")
@login_required
def logout():
    logout_user()

    if 'next' not in request.args:
        next_url = url_for('index')
    else:
        if request.args.get('next') == '':
            next_url = url_for('index')
        else:
            from .utils import get_safe_redirect
            next_url = get_safe_redirect(request.args.get('next'))
    return redirect(next_url)


@bp.route("/get-user")
@login_required
def getUser():
    if (request.accept_mimetypes.best == "application/json"):
        return jsonify(dict(user = dict(name=current_user.name, rollNo=current_user.rollNo, email=current_user.email, profilePic=current_user.profilePic)))
    else:
        raise NotFound()
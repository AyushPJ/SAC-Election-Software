from flask import Blueprint, jsonify
from flask import request, render_template
from flask_login import current_user
from psycopg2 import IntegrityError
from .utils import admin_required
from .db import get_db
from re import fullmatch

bp = Blueprint("admin", "admin", url_prefix="/admin")


@bp.route('/')
@admin_required
def index():
    return render_template('admin/index.html')

@bp.route('/test')
@admin_required
def test():
    return (
        "<p>Hello, {}! You're logged in! Email: {}</p>"
        "<div><p>Google Profile Picture:</p>"
        '<img src="{}" alt="Google profile pic"></img></div>'
        '<a class="button" href="/auth/logout?next=http://localhost:5000/auth/login/admin">Logout</a>'.format(
            current_user.name, current_user.email, current_user.profilePic
        )
    )

@bp.route('/posts/add', methods=["POST"])
@admin_required
def addPosts():
    if (request.accept_mimetypes.best == "application/json"):
        post = request.json.get('post')
        if type(post) == type(""):
            post = fullmatch(r'^[a-zA-Z ]+$', post).group(0)
            conn = get_db()
            cursor = conn.cursor()
            try:
                cursor.execute("insert into posts(position) values(%s)", (post,))
            except IntegrityError:
                return {"msg": "Post already exists"}, 200
            conn.commit()
            conn.close()
            return "OK", 200
        else:
            return "Invalid request format", 400
    
@bp.route('/posts/remove', methods=["POST"])
@admin_required
def removePosts():
    if (request.accept_mimetypes.best == "application/json"):
        posts = request.json.get('posts')
        if type(posts) == type([]):
            conn = get_db()
            cursor = conn.cursor()
            for post in posts:
                cursor.execute("delete from posts where position = %s", (post,))
            conn.commit()
            conn.close()
            return "OK", 200
        else:
            return "Invalid request format", 400

@bp.route('/fetch-student', methods=["POST"])
#@admin_required
def fetchStudent():
    if (request.accept_mimetypes.best == "application/json"):
        rollNo = request.json.get('rollNo')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("select * from nitc_students where roll_no = %s", (rollNo,))
        student = cursor.fetchone()
        conn.close()
        if(student == None):
            return {"msg":"Does not exist"}, 200
        else:
            return jsonify(dict(student = dict(rollNo=student[0], name=student[1], phoneNo=student[2], email=student[3], eligibility=student[4])))
    else:
        return "Invalid request format", 400

@bp.route('/change-eligibility', methods=["POST"])
@admin_required
def changeEligibility():
    if (request.accept_mimetypes.best == "application/json"):
        rollNo = request.json.get('rollNo')
        eligibility = request.json.get('eligibility')
        conn = get_db()
        cursor = conn.cursor()
        adminID = current_user.get_adminID()
        cursor.execute("update nitc_students set eligibility_status=%s, admin_id = %s where roll_no = %s", (eligibility, adminID, rollNo))
        conn.commit()
        conn.close()
        return "OK", 200
    else:
        return "Invalid request format", 400
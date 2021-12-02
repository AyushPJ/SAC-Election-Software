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
            return "invalid request", 404
    
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
            return "invalid request", 404

@bp.route('/fetch-student', methods=["POST"])
@admin_required
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
        return "invalid request", 404

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
        return "invalid request", 404

@bp.route('/get-applications/<post>', methods=["GET"])
@admin_required
def getApplications(post):
    if (request.accept_mimetypes.best == "application/json"):
        conn = get_db()
        cursor = conn.cursor()
        if (post=="All"):
            cursor.execute("select * from applicants where application_status=%s", ("waiting",))
        else:
            cursor.execute("select * from applicants where application_status=%s and position=%s", ("waiting",post))
        applications = cursor.fetchall()
        apps = []
        for application in applications:
            appNo = application[0]
            cursor.execute("select * from applies_for where application_no = %s", (appNo,))
            rollNo = cursor.fetchone()[0]
            cursor.execute("select * from nitc_students where roll_no = %s", (rollNo,))
            student = cursor.fetchone()
            apps.append(dict(rollNo = student[0], name= student[1], phoneNo = student[2], email = student[3], applicationNo = application[0], position=application[1], cgpa=application[2]))
        conn.commit()
        conn.close()
        return jsonify(dict(applications = apps))
    else:
        return "invalid request", 404


@bp.route('/change-status', methods=["POST"])
@admin_required
def changeStatus():
    if (request.accept_mimetypes.best == "application/json"):
        conn = get_db()
        cursor = conn.cursor()
        apps = request.json.get('applications')
        adminID = current_user.get_adminID()
        for app in apps:
            appNo = app['applicationNo']
            status = app['status']
            if status == "accept":
                cursor.execute("update applicants set application_status=%s, admin_id=%s where application_no = %s", ("accepted",adminID, appNo))
                cursor.execute("insert into candidates (application_no) values (%s)", (appNo,))
            else:
                cursor.execute("update applicants set application_status=%s, admin_id=%s where application_no = %s", ("rejected", adminID, appNo))

        conn.commit()
        conn.close()
        return "OK", 200
    else:
        return "invalid request", 404

@bp.route('/election-statistics', methods=["GET"])
@admin_required
def electionStatistics():
    if (request.accept_mimetypes.best == "application/json"):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("select n.name, c.votes, a.position from candidates c, appicants a, applies_for f, voters v, nitc_students n where c.application_no = a.application_no and a.application_no = f.application_no and f.roll_no = v.roll_no and v.roll_no = n.roll_no group by a.position")
        candidates = cursor.fetchall()
        votes = []
        pos = candidates[0][2]
        ind = []
        for candidate in candidates:
            if pos == candidate[2]:
                ind.append(dict(name = candidate[0], votes = candidate[1]))
            else:
                votes.append(dict(position = pos))
                pos = candidate[2]
        conn.commit()
        conn.close()
        return jsonify(dict(electionStats = votes))
    else:
        return "invalid request", 404
        





from flask import Blueprint, app, request, jsonify
from werkzeug.utils import append_slash_redirect
from .utils import student_required
from .db import get_db
from flask_login import current_user


bp = Blueprint("applications", "applications", url_prefix="/applications")

@bp.route("/get-posts")
def getPosts(isHTTP=True):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from posts")
    posts = cursor.fetchall()
    posts = [post[0] for post in posts]
    if (request.accept_mimetypes.best == "application/json" and isHTTP):
        return jsonify(dict(posts = posts))
    elif (not isHTTP):
        return posts

@bp.route("/get")
@student_required
def getApplications():
    if (request.accept_mimetypes.best == "application/json"):
        conn = get_db()
        cursor = conn.cursor()
        rollNo = current_user.rollNo
        cursor.execute("select application_no from applies_for where roll_no = %s", (rollNo,))
        appNos = [apps[0] for apps in cursor.fetchall()]
        waitingApps = []
        rejectedApps = []
        acceptedApps = []
        for appNo in appNos:
            cursor.execute("select * from applicants where application_no = %s", (appNo,))
            application = cursor.fetchone()
            adminID = application[4]
            adminName = ''
            if not adminID == None:
                cursor.execute("select name from admins where admin_id = %s", (adminID,))
                adminName = cursor.fetchone()[0]
            applicationStatus = application[3]
            if applicationStatus == "waiting":
                waitingApps.append(dict(applicationNo = application[0], position = application[1], cgpa = application[2], applicationStatus = application[3], adminName = adminName))
            elif applicationStatus == "accepted":
                acceptedApps.append(dict(applicationNo = application[0], position = application[1], cgpa = application[2], applicationStatus = application[3], adminName = adminName))
            elif applicationStatus == "rejected":
                rejectedApps.append(dict(applicationNo = application[0], position = application[1], cgpa = application[2], applicationStatus = application[3], adminName = adminName))
        return jsonify(dict(applications = dict(accepted=acceptedApps, rejected=rejectedApps, waiting=waitingApps)))
        
    else:
        return "invalid request", 404

@bp.route("/submit", methods=["POST"])
@student_required
def submitApplication():
    if (request.accept_mimetypes.best == "application/json"):
        cgpa = request.json.get('cgpa')
        pos = request.json.get('position')
        if cgpa == None or pos == None:
            return "Invalid request format" , 400
        try:
            cgpa = float(cgpa)
        except ValueError:
            return "Invalid request format" , 400

        cgpa = round(cgpa, 2)
        if (pos not in getPosts(isHTTP=False)):
            return "Invalid request format" , 400

        conn = get_db()
        cursor = conn.cursor()
        rollNo = current_user.rollNo
        cursor.execute("insert into applicants(position, cgpa, application_status) values(%s,%s,%s)", (pos, cgpa, "waiting"))
        cursor.execute("select application_no from applicants order by application_no desc limit 1");
        appNo = cursor.fetchone()[0]
        cursor.execute("insert into applies_for(roll_no, application_no) values(%s,%s)", (rollNo, appNo))
        conn.commit()
        conn.close()
        return "OK", 200
    else:
        return "invalid request", 404
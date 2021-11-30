from flask import Blueprint, request
from .utils import student_required
from .db import get_db
from flask_login import current_user

bp = Blueprint("applications", "applications", url_prefix="/applications")


@bp.route("/get")
@student_required
def getApplications():
    if (request.accept_mimetypes.best == "application/json"):
        conn = get_db()
        cursor = conn.cursor()
        rollNo = current_user.rollNo[0]
        cursor.execute("select * from applies_for where roll_no = %s", (rollNo,))
        appNos = cursor.fetchall()
        print(appNos)
        return "OK", 200
    else:
        return "invalid request", 404

@bp.route("/submit", methods=["POST"])
@student_required
def submitApplication():
    if (request.accept_mimetypes.best == "application/json"):
        cgpa = request.json['cgpa']
        pos = request.json['position']
        print(cgpa, pos)
        conn = get_db()
        cursor = conn.cursor()
        rollNo = current_user.rollNo[0]
        cursor.execute("select * from applies_for where roll_no = %s", (rollNo,))
        appNos = cursor.fetchall()
        print(appNos)
        return "OK", 200
    else:
        return "invalid request", 404
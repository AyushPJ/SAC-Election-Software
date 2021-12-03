import datetime
from flask import Blueprint
from flask import request, jsonify, redirect
from flask.helpers import url_for
from werkzeug.exceptions import NotFound
from flask_login import current_user
from .utils import student_required, voting_required

from . import db
bp = Blueprint("vote", "vote", url_prefix="/vote")


@bp.route('/voting-page')
@student_required
@voting_required
def getVotingPage():
    return redirect("http://localhost:3000")


@bp.route("/get-candidates/<post>", methods=["GET"])
@student_required
@voting_required
def getCandidates(post):
    if (request.accept_mimetypes.best == "application/json"):
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("select c.application_no, n.roll_no, n.name, a.position from candidates c, applicants a, applies_for f, nitc_students n where c.application_no = a.application_no and a.application_no = f.application_no and f.roll_no = n.roll_no and a.position = %s",(post,))
        candidates = cursor.fetchall()
        return jsonify(dict(candidates = [dict(applicationNo=appNo, rollNo = rollNo, name = name, post = post) for appNo, rollNo, name, post in candidates]))
    else:
        raise NotFound()


@bp.route("/submit", methods=["POST"])
@student_required
@voting_required
def submitVote():
    if (request.accept_mimetypes.best == "application/json"):
        votes = request.json.get('votes')
        print(votes)
        if votes:
            conn = db.get_db()
            cursor = conn.cursor()
            postsVoted = dict()
            candidatesVoted = dict()
            validVote = True
            for vote in votes:
                if vote['applicationNo'] == -1:
                    postsVoted[vote['post']] = True
                else:
                    cursor.execute("select c.application_no, a.position from candidates c, applicants a where c.application_no = %s and c.application_no = a.application_no",(vote['applicationNo'],))
                    candidate = cursor.fetchone()
                    if not candidate:
                        validVote = False
                        break
                    if candidate[0] in candidatesVoted:
                        validVote = False
                        break
                    if candidate[1] in postsVoted:
                        validVote = False
                        break
                    candidatesVoted[candidate[0]] = True
                    postsVoted[candidate[1]] = True
                    cursor.execute("update candidates set votes = votes + 1 where application_no = %s",(candidate[0],))
            if validVote == True:
                cursor.execute("update voters set voting_status = true where roll_no = %s", (current_user.rollNo,))
                conn.commit()
                return "OK", 200
            else:
                conn.close()
                return ("Invalid request format",400)
        return ("Invalid request format",400)
               
    return NotFound()


    

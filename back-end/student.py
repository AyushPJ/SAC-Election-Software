from flask import Blueprint, jsonify
from flask import request, render_template, current_app
from flask_login import current_user
from flask_login.utils import logout_user
from werkzeug.exceptions import NotFound
from .utils import student_required
from datetime import datetime

from . import db

bp = Blueprint("student", "student", url_prefix="/student")


@bp.route('/index')
@student_required
def index():
    appStatus = current_app.config['APPLICATIONS']
    voteStatus = current_app.config['VOTING']
    from .vote import getVotingPage
    from .applications import getApplicationsPage
    if appStatus['status']:
        return getApplicationsPage()
    elif appStatus['status'] == "Automatic":
        currentDT = datetime.utcnow()
        if((appStatus['open'] and appStatus['open'] <= currentDT) or not appStatus['open']):
            if ((appStatus['close'] and currentDT <= appStatus['close']) or not appStatus['close']):
                return getApplicationsPage()
    if voteStatus['status']:
        return getVotingPage()
    elif voteStatus['status'] == "Automatic":
        currentDT = datetime.utcnow()
        if((voteStatus['open'] and voteStatus['open'] <= currentDT) or not voteStatus['open']):
            if ((voteStatus['close'] and currentDT <= voteStatus['close']) or not voteStatus['close']):
                return getVotingPage()
    logout_user()
    return render_template('error.html', msg="Elections are closed now. Please check back later", title="Unavailable", statusCode="401")


@bp.route('/election-results', methods=["GET"])
def electionResults():
    if (request.accept_mimetypes.best == "application/json"):
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT roll_no, name, position, max(votes) \
                        FROM (((SELECT application_no, votes FROM candidates)q1 \
                            NATURAL JOIN (SELECT application_no, position FROM applicants)q2) \
                                NATURAL JOIN (select application_no,roll_no from applies_for)q3)q4 \
                                    NATURAL JOIN (select name, roll_no from nitc_students)q5 \
                        GROUP BY position, roll_no, name, votes \
                        ORDER BY votes desc")
        candidates = cursor.fetchall()
        votes = []
        if (len(candidates)>0):  
            pos = candidates[0][2]
            ind = []
            for candidate in candidates:
                if pos == candidate[2]:
                    ind.append(dict(rollNo = candidate[0], name = candidate[1], votes = candidate[3]))
                else:
                    votes.append(dict(position = pos, candidates = ind))
                    ind = []
                    pos = candidate[2]
                    ind.append(dict(rollNo = candidate[0], name = candidate[1], votes = candidate[3]))
            
            if(len(ind)>0):
                votes.append(dict(position = pos, candidates = ind))

        cursor.execute("select count(*) from voters");
        totalVoters = cursor.fetchone()[0];
        cursor.execute("select count(*) from voters where voting_status=%s", (True,));
        voted = cursor.fetchone()[0]

        conn.close()
        return jsonify(dict(allCandidates = votes, voters=dict(total=totalVoters,voted=voted)))
    else:
        raise NotFound()
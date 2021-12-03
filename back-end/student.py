from flask import Blueprint, jsonify
from flask import  render_template, current_app
from flask_login.utils import logout_user
from werkzeug.exceptions import NotFound
from .utils import student_required
from datetime import datetime

from . import db
from .utils import applicationsPageOpen, votingPageOpen
bp = Blueprint("student", "student", url_prefix="/student")




@bp.route('/index')
@student_required
def index():
    from .vote import getVotingPage
    from .applications import getApplicationsPage
    if (votingPageOpen()):
        return getVotingPage()
    elif (applicationsPageOpen()):
        return getApplicationsPage()
    logout_user()
    return render_template('error.html', msg="Elections are closed now. Please check back later", title="Unavailable", statusCode="401")


@bp.route('/election-results', methods=["GET"])
def electionResults():
    flag = 0
    if votingPageOpen():
        flag = 1
    elif applicationsPageOpen():
        flag = 2
    votes = []
    conn = db.get_db()
    cursor = conn.cursor()
    if flag == 2:
        return render_template('error.html', msg="Applications are going on. Please check back later", title="Unavailable", statusCode="401")
    elif not flag:
        cursor.execute("SELECT roll_no, name, position, max(votes) \
                        FROM (((SELECT application_no, votes FROM candidates)q1 \
                            NATURAL JOIN (SELECT application_no, position FROM applicants)q2) \
                                NATURAL JOIN (select application_no,roll_no from applies_for)q3)q4 \
                                    NATURAL JOIN (select name, roll_no from nitc_students)q5 \
                        GROUP BY position, roll_no, name, votes \
                        ORDER BY votes desc")
        candidates = cursor.fetchall()
        
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
    voterTurnout = "0.00%"
    if totalVoters:
        voterTurnout = str(round((voted/totalVoters)*100, 2))+"%"
    return render_template('election-results.html', allCandidates = votes, totalVoters=str(totalVoters), voted=str(voted), voterTurnout=voterTurnout)
  
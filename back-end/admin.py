from flask import Blueprint, app, jsonify
from flask import request, render_template, current_app
from flask_login import current_user
from psycopg2 import IntegrityError
from werkzeug.utils import redirect
from .utils import admin_required
from .db import get_db
from re import fullmatch
from datetime import datetime
from werkzeug.exceptions import NotFound

bp = Blueprint("admin", "admin", url_prefix="/admin")


@bp.route('/')
@admin_required
def index():
    return redirect("http://localhost:3002")

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
            return "OK", 200
        else:
            raise NotFound()
    
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
            return "OK", 200
        else:
            raise NotFound()

@bp.route('/fetch-student', methods=["POST"])
@admin_required
def fetchStudent():
    if (request.accept_mimetypes.best == "application/json"):
        rollNo = request.json.get('rollNo')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("select * from nitc_students where roll_no = %s", (rollNo,))
        student = cursor.fetchone()
        if(student == None):
            return {"msg":"Does not exist"}, 200
        else:
            return jsonify(dict(student = dict(rollNo=student[0], name=student[1], phoneNo=student[2], email=student[3], eligibility=student[4])))
    else:
        raise NotFound()

@bp.route('/change-eligibility', methods=["POST"])
@admin_required
def changeEligibility():
    if (request.accept_mimetypes.best == "application/json"):
        rollNo = request.json.get('rollNo')
        eligibility = request.json.get('eligibility')
        conn = get_db()
        cursor = conn.cursor()
        adminID = current_user.get_adminID()
        cursor.execute("delete from users where roll_no = %s", (rollNo,))
        cursor.execute("update nitc_students set eligibility_status=%s, admin_id = %s where roll_no = %s", (eligibility, adminID, rollNo))
        conn.commit()
        return "OK", 200
    else:
        raise NotFound()

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
        return jsonify(dict(applications = apps))
    else:
        raise NotFound()


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
        return "OK", 200
    else:
        raise NotFound()

@bp.route('/election-statistics', methods=["GET"])
@admin_required
def electionStatistics():
    if (request.accept_mimetypes.best == "application/json"):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT roll_no, name, position, votes \
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
        return jsonify(dict(allCandidates = votes, voters=dict(total=totalVoters,voted=voted)))
    else:
        raise NotFound()
        

@bp.route('/get-site-status', methods=["GET"])
@admin_required
def getSiteStatus():
    if (request.accept_mimetypes.best == "application/json"):
        return jsonify(dict(applications=current_app.config['APPLICATIONS'], voting=current_app.config['VOTING']))
    else:
        raise NotFound()

@bp.route('/change-site-status', methods=["POST"])
@admin_required
def changeSiteStatus():
    if (request.accept_mimetypes.best == "application/json"):
       try:
            method = request.json.get('method')
            newAppState = current_app.config['APPLICATIONS']
            newVoteState = current_app.config['VOTING']
            if (method == "manual"):
                newAppState['status'] = False
                newAppState['open'] = None
                newAppState['close'] = None
                newVoteState['status'] = False
                newVoteState['open'] = None
                newVoteState['close'] = None
                toOpen = request.json.get('toOpen')
                if (toOpen == "applications"):
                    newAppState['status'] = True
                elif (toOpen == "voting"):
                    newVoteState['status'] = True

            elif (method == "automatic"):
                appOpen = request.json.get('appOpen')
                appClose = request.json.get('appClose')
                voteOpen = request.json.get('voteOpen')
                voteClose = request.json.get('voteClose')
                currentDateTime = datetime.utcnow()
                if (appOpen):
                    appOpen = datetime.strptime(appOpen[:-5], "%Y-%m-%dT%H:%M:%S")
                    if (appOpen <currentDateTime):
                        return {"msg":"Bad application open time."}, 200
                else:
                    appOpen = newAppState['open']

                if (appClose):
                    appClose = datetime.strptime(appClose[:-5], "%Y-%m-%dT%H:%M:%S")
                    if (appClose <currentDateTime):
                        return {"msg":"Bad application close time."}, 200
                else:
                    appClose = newAppState['close']

                if (voteOpen):
                    voteOpen = datetime.strptime(voteOpen[:-5], "%Y-%m-%dT%H:%M:%S")
                    if (voteOpen<currentDateTime):
                        return {"msg":"Bad voting open time."}, 200  
                else:
                    voteOpen = newVoteState['open']

                if (voteClose):
                    voteClose = datetime.strptime(voteClose[:-5], "%Y-%m-%dT%H:%M:%S")
                    if (voteClose < currentDateTime):
                        return {"msg":"Bad voting close time."}, 
                else:
                    voteClose = newVoteState['close']
                
                if (appClose):
                    if (appOpen and appClose < appOpen):
                        return {"msg":"Bad application close time."}, 200        
                if (voteOpen):
                    if (appClose and voteOpen < appClose):
                        return {"msg":"Bad voting open time."}, 200       
                    elif (appOpen):
                        if (voteOpen < appOpen):
                            return {"msg":"Bad voting open time."}, 200
                        elif (not appClose):
                            appClose = voteOpen

                if (voteClose):
                    if (voteOpen and voteClose < voteOpen):
                        return {"msg":"Bad voting close time."}, 200
                    elif (appClose):
                        if (voteClose < appClose):
                            return {"msg":"Bad voting close time."}, 200
                        elif (not voteOpen):
                            voteOpen = appClose
                    elif (appOpen):
                        return {"msg":"Bad voting close time."}, 200

                newAppState['status'] = "Automatic"
                newAppState['open'] = appOpen
                newAppState['close'] = appClose
                newVoteState['status'] = "Automatic"
                newVoteState['open'] = voteOpen
                newVoteState['close'] = voteClose

                current_app.config['APPLICATIONS'] = newAppState
                current_app.config['VOTING'] = newVoteState

            elif method == "close":
                current_app.config['APPLICATIONS'] = dict(status=False,open = None, close = None)
                current_app.config['VOTING'] = dict(status=False,open = None, close = None)
            return "OK", 200
       except ValueError or AttributeError:
           return "Invalid request format", 400
      
        
    else:
        raise NotFound()


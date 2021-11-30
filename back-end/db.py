import psycopg2

from faker import Faker
import random

import click 
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g: # If we've not initialised the database, then
                      # initialise it
        # Notice how we take the name of the database from the
        # config. We initialised this in the __init__.py file.
        dbname = current_app.config['DATABASE_NAME'] 
        g.db = psycopg2.connect(dbname=dbname)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    fake = Faker(['en_IN'])
    db = get_db()
    f = current_app.open_resource("sql/create.sql")
    sql_code = f.read().decode("ascii")
    cur = db.cursor()
    cur.execute(sql_code)
    
    for i in range(20):
        name = fake.name()
        rollNo = fake.unique.random_int(min=170000, max=219999)

        rollNo = random.choice(['B','M','P']) + str(rollNo) + random.choice(['CS','ME','EC','EE','CE'])
        fname = name.split(' ')[0]
        nitc_email = fname.lower()+'_'+rollNo.lower()+'@nitc.ac.in'
        phone_no = fake.phone_number()[-10:]
        cur.execute("insert into nitc_students(roll_no,name,phone_no,nitc_email) values (%s,%s,%s,%s)",(rollNo,name,phone_no,nitc_email))
    
    import json

    testDataJSON = open('sql/test_data.json', 'r')
    testData = json.load(testDataJSON)
    testDataJSON.close()

    for student in testData['students']:
        cur.execute("insert into nitc_students(roll_no,name,phone_no,nitc_email) values (%s,%s,%s,%s)",(student['roll_no'],student['name'],student['phone_no'],student['nitc_email']))
        cur.execute("insert into voters(roll_no) values (%s)",(student['roll_no'],))

    for admin in testData['admins']:
        cur.execute("insert into admins(name,phone_no,email) values (%s,%s,%s)",(admin['name'],admin['phone_no'],admin['email']))

    for position in testData['posts']:
        cur.execute("insert into posts(position) values (%s)",(position,))

    cur.close()
    db.commit()
    close_db()


# All flask commands cannot be run separately. If we simply import this file and try to run things, it will not work since flask creates a "context" for everything to run (e.g. g, current_app etc.). The with_appcontext decorator adds this context before running the init_db_command
@click.command('initdb', help="initialise the database") # If we run "flask initdb", this function will run.
@with_appcontext
def init_db_command():
    init_db()
    click.echo('DB initialised') # This the click library API to print a message on the screen


# All commands and other things need to be registered into the
# application. We write a function here that can be called inside
# __init__.py which will add the init_db_command to the CLI. If you
# run flask --help now, you will see the initidb command there. Also,
# we add a "hook" to automatically call close_db when the app finishes
# execution. This will make sure that database connections are closed
# when done.
def init_app(app):
    app.teardown_appcontext(close_db) #hook
    app.cli.add_command(init_db_command)


from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, rollNo, name, email, profilePic, admin):
        self.id = id
        self.rollNo = rollNo
        self.name = name
        self.email = email
        self.profilePic = profilePic
        self.admin = admin

    def get_id(self):
        return self.id

    def get_adminID(self):
        if not self.admin:
            return None
        from .db import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT admin_id FROM admins WHERE email = %s", (self.email,))
        adminID = cursor.fetchone()[0]
        return adminID

    def get_votingStatus(self):
        if self.admin:
            return None
        from .db import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT voting_status FROM voters WHERE roll_no = %s", (self.rollNo,))
        status = cursor.fetchone()[0]
        return status

    @staticmethod
    def get(userID):
        from .db import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (userID,))
        user = cursor.fetchone()
        if not user:
            return None
        user = User(id=user[0], rollNo=user[1], name=user[2], email=user[3], profilePic=user[4], admin=user[5])

        return user


    @staticmethod
    def createStudent(id, name, email, profilePic):
        from .db import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * from nitc_students where nitc_email = %s", (email, ))
        student = cursor.fetchone()
        if student == None:
            return -1
        if not student[4]:
            return -2
        rollNo = student[0]
        cursor.execute(
            "INSERT INTO users (id, roll_no, name, email, profile_pic, admin) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (id, rollNo, name, email, profilePic, False),
        )

        conn.commit()
        return 0

    @staticmethod
    def createAdmin(id, name, email, profilePic):
        from .db import get_db
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * from admins where email = %s", (email, ))
        admin = cursor.fetchone()
        if admin == None:
            return -1

        cursor.execute(
            "INSERT INTO users (id, name, email, profile_pic, admin) "
            "VALUES (%s,%s,%s,%s,%s)",
            (id, name, email, profilePic, True),
        )

        conn.commit()
        return 0
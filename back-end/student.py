from flask import Blueprint
from flask import request, render_template, redirect, url_for
from flask_login import current_user
from .utils import student_required


bp = Blueprint("student", "student", url_prefix="/student")


@bp.route('/dashboard')
@student_required
def dashboard():
    return (
        "<p>Hello, {}! You're logged in! Email: {}</p>"
        "<div><p>Google Profile Picture:</p>"
        '<img src="{}" alt="Google profile pic"></img></div>'
        '<a class="button" href="/auth/logout?next=http://localhost:5000/auth/login/student">Logout</a>'.format(
            current_user.name, current_user.email, current_user.profilePic
        )
    )  
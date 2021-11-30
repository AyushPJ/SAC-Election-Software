from flask import Blueprint
from flask import request, render_template, redirect, url_for
from flask_login import current_user
from .utils import admin_required


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
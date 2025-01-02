from flask import Blueprint
from flask import request, redirect, render_template, session, url_for
import app_config
import services.identity as idt
import services.users_service as users_service
from models.models import User

auth_router = Blueprint('auth', __name__, template_folder="../template/")

@auth_router.route("/")
@auth_router.route("/login")
def login():
    url = idt.get_authorization_url()
    print(url)
    return render_template("login.html", auth_uri=url)

@auth_router.route(app_config.REDIRECT_PATH)
def auth_response():
    code = idt.get_code(request)
    state = idt.get_state(request)
    token = idt.get_token(code, state)
    # create the user profile in the database
    user = idt.get_user_info(token)
    if not user:
        return redirect(url_for("auth.login"))
    if not User.query.filter_by(userName=user["preferred_username"]).first():
        users_service.create_user_from_profile_token(user)
    return redirect(url_for(".index"))

@auth_router.route("/logout")
def logout():
    return redirect(idt.log_out(url_for(".index", _external=True)))

@auth_router.route("/index")
def index():
    user = idt.get_user_info(session.get("token"))
    if not user:
        return redirect(url_for("auth.login"))
    return render_template("index.html", user=user)

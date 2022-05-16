from flask import Blueprint, render_template

blueprint_home = Blueprint("home", __name__)


@blueprint_home.route("/")
def home():
    return render_template("home.html")

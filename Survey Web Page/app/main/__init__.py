from flask import Blueprint
from flask import render_template

bp = Blueprint('main', __name__, template_folder='templates')

@bp.route('/')
def home():
    return render_template('main/home.html')
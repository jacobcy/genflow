from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/about')
def about():
    return 'About Page'
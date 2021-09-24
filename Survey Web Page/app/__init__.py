from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


# Application configuration class
class MainConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://yuste:yuste@localhost/Survey'
    SECRET_KEY = "yuste"
    ENVIRONMENT = 'development'
    DEBUG = True


def create_app():
    app = Flask(__name__)
    app.config.from_object(MainConfig)
    #login_manager = LoginManager()
    db.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        from . import auth
        from .survey import bp as survey_bp
        from .main import bp as main_bp
        from . import errors
        from . import model
        @login_manager.user_loader
        def load_user(user_id):
            return model.User.query.get(int(user_id))


        app.register_error_handler(404, errors.handle_404)
        app.register_error_handler(403, errors.handle_403)
        app.register_error_handler(500, errors.handle_500)

        app.register_blueprint(main_bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(survey_bp)

        return app




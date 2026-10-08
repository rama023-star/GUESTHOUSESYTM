"""GuestFlow Flask application factory."""
from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "error"
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app import models  # noqa: F401
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.input import input_bp
    from app.reports import reports_bp
    from app.manage import manage_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(input_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(manage_bp)

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("error.html", code=500, message="Something went wrong"), 500

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("error.html", code=403, message="You do not have access to this page"), 403

    @app.get("/health")
    def health():
        from sqlalchemy import text
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ok"), 200

    @app.context_processor
    def inject_settings():
        return {"currency_code": app.config["CURRENCY_CODE"]}

    return app


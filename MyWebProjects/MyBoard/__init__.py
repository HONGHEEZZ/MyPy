from flask import Flask

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)

    # @app.route("/")
    # def hello():
    #     return "Hello World..."

    from views import main_views
    app.register_blueprint(main_views.bp)

    return app

if __name__ == "__main__":
    app=create_app()
    app.run(debug=True)

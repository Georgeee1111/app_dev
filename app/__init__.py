from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'app_dev'

    mysql.init_app(app)

    # Import blueprints here to avoid circular imports
    from app.authroutes import auth
    from app.routes import main

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app

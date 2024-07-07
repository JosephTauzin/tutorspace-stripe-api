from os import environ
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_swagger_ui import get_swaggerui_blueprint
from config.swagger_config import swagger_template
from dotenv import load_dotenv
from controllers import payments, membership, payroll, company, webhook, coupon

import firebase_admin
from firebase_admin import credentials

load_dotenv()


def initialize_firebase():
    try:
        cred = credentials.Certificate(environ["FIREBASE_CREDENTIALS_PATH"])
        firebase_admin.initialize_app(cred, {
            "databaseURL": environ["DATABASE_URL"]
        })
    except Exception as error:
        print(error)


def create_app():
    initialize_firebase()
    app = Flask(__name__)
    CORS(app)
    app.config.from_object("config.settings")

    swagger = Swagger(app, template=swagger_template)

    app.register_blueprint(payments)
    app.register_blueprint(membership)
    app.register_blueprint(company)
    app.register_blueprint(payroll)
    app.register_blueprint(webhook)
    app.register_blueprint(coupon)

    ui = get_swaggerui_blueprint(
        base_url="/swagger-ui",
        api_url="/"
    )

    app.register_blueprint(ui, url_prefix=None)

    return app

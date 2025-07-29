# sampah/web.py
from flask import Flask, render_template
import os

def create_app():
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    static_dir = os.path.join(os.path.dirname(__file__), "static")

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    @app.route("/")
    def home():
        return render_template("index.html")

    return app

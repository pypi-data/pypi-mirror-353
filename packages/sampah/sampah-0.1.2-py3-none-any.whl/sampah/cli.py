# sampah/cli.py
from sampah.web import create_app

def main():
    app = create_app()
    app.run(debug=True, port=5000)

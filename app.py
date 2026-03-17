from flask import Flask, render_template

import config
from models.database import init_db
from routes.entries import entries_bp
from routes.analytics import analytics_bp
from routes.music import music_bp

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

app.register_blueprint(entries_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(music_bp)


@app.route("/")
def index():
    return render_template("index.html")


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)

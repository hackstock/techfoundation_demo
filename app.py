from flask import Flask, redirect, render_template, request, url_for, jsonify 
from flask_sqlalchemy import SQLAlchemy
import os 

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__) 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "data.sqlite")
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True

db = SQLAlchemy(app)

class CoronaRecord(db.Model):
    __tablename__ = "corona_records"
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(20), unique=True, index=True)
    country = db.Column(db.String(20))
    confirmed = db.Column(db.Integer)
    dead = db.Column(db.Integer)
    recovered = db.Column(db.Integer)

    def to_json(self):
        return {
            "id": self.id,
            "city": self.city,
            "country": self.country,
            "confirmed": self.confirmed,
            "dead": self.dead,
            "recovered": self.recovered
        }


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

@app.route("/contact")
def contact_us():
    return render_template("contact.html")

@app.route("/")
def index():
    page_title = "Corona 2020 Dashboard"
    records = CoronaRecord.query.all()
    return render_template(
        "home.html",
        dashboard_title=page_title,
        records=records
    )

@app.route("/save", methods=["POST"])
def save():
    c = CoronaRecord()
    c.city = request.form["city"]
    c.country = request.form["country"]
    c.confirmed = int(request.form["confirmed"])
    c.dead = int(request.form["dead"])
    c.recovered = int(request.form["recovered"])

    db.session.add(c)
    db.session.commit()

    return redirect(url_for('index'))

@app.route("/api/welcome", methods=["GET"])
def api_index():
    resp = {
        "version": "0.0.1",
        "author": "Tech Foundation",
        "email": "devs@techfoundation.org"
    }

    return jsonify(data=resp)

@app.route("/api/records", methods=["POST"])
def create_record():
    payload = request.get_json()

    c = CoronaRecord()
    c.city = payload["city"]
    c.country = payload["country"]
    c.confirmed = int(payload["confirmed"])
    c.dead = int(payload["dead"])
    c.recovered = int(payload["recovered"])

    db.session.add(c)
    db.session.commit()

    return jsonify(data=c.to_json())

@app.route("/api/records", methods=["GET"])
def get_records():
    records = CoronaRecord.query.all()
    resp = [r.to_json() for r in records]
    return jsonify(data=resp)

@app.route("/api/search", methods=["GET"])
def search_records():
    nation = request.args["c"]
    records = CoronaRecord.query.filter_by(country=nation)
    resp = [r.to_json() for r in records]

    return jsonify(data=resp)

@app.route("/api/delete", methods=["POST"])
def delete_record():
    payload = request.get_json()
    id = int(payload["id"])
    record = CoronaRecord.query.get(id)
    db.session.delete(record)
    db.session.commit()

    resp = {
        "msg": "Record deleted successfully",
        "id": id
    }

    return jsonify(data=resp)

@app.route("/api/update", methods=["POST"])
def update_record():
    payload = request.get_json()
    id = int(payload["id"])

    record = CoronaRecord.query.get(id)

    record.city = payload["city"]
    record.country = payload["country"]
    record.confirmed = int(payload["confirmed"])
    record.dead = int(payload["dead"])
    record.recovered = int(payload["recovered"])

    db.session.add(record)
    db.session.commit()

    return jsonify(data=record.to_json())


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        debug=True,
        port=5000
    )


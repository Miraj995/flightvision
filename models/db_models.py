from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    arrival = db.Column(db.String(100), nullable=False)
    departure = db.Column(db.String(100), nullable=False)
    gate = db.Column(db.String(10))
    baggage_belt = db.Column(db.String(10))

    def __repr__(self):
        return f"<Flight {self.flight_number}>"

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    media_url = db.Column(db.String(255), nullable=False)
    media_type = db.Column(db.String(10), nullable=False)  # 'image' or 'video'

    def __repr__(self):
        return f"<Ad {self.title}>"

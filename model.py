from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

#User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")

class StudentApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref="applications")

    # Personal Info
    father_name = db.Column(db.String(150), nullable=False)
    mother_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)

    # Academic Info
    tenth_year = db.Column(db.Integer, nullable=False)
    tenth_marks = db.Column(db.Float, nullable=False)
    twelfth_year = db.Column(db.Integer, nullable=False)
    twelfth_marks = db.Column(db.Float, nullable=False)

    # Documents stored as binary
    degree_certificate_name = db.Column(db.String(200), nullable=False)
    degree_certificate_data = db.Column(db.LargeBinary, nullable=False)

    id_proof_name = db.Column(db.String(200), nullable=True)
    id_proof_data = db.Column(db.LargeBinary, nullable=True)

    status = db.Column(db.String(20), default="Pending")

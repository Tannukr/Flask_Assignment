from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
import re

from config import Config
from model import *
from student_route import register_offer_letter_routes


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
mail = Mail(app)

app.config["JWT_SECRET_KEY"] = "your-secret-key"
jwt = JWTManager(app)


register_offer_letter_routes(app)



def validate_email(email):
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(regex, email) is not None



@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')

    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(name=name, email=email, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "role": role}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid password"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "token": access_token,
            "role": user.role
        }
    }), 200


@app.route('/api/application', methods=['POST'])
@jwt_required()
def submit_application():
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    if claims["role"] != "student":
        return jsonify({"error": "Only students can submit applications"}), 403

    data = request.get_json()
    new_app = StudentApplication(
        user_id=current_user_id,
        father_name=data.get("father_name"),
        mother_name=data.get("mother_name"),
        phone=data.get("phone"),
        address=data.get("address"),
        tenth_year=data.get("tenth_year"),
        tenth_marks=data.get("tenth_marks"),
        twelfth_year=data.get("twelfth_year"),
        twelfth_marks=data.get("twelfth_marks"),
        degree_certificate=data.get("degree_certificate"),
        id_proof=data.get("id_proof")
    )
    db.session.add(new_app)
    db.session.commit()

    return jsonify({"message": "Application submitted successfully"}), 201


@app.route('/api/applications', methods=['GET'])
@jwt_required()
def get_all_applications():
    claims = get_jwt()

    if claims["role"] != "admin":
        return jsonify({"error": "Only admins can view applications"}), 403

    applications = StudentApplication.query.all()
    result = []
    for app_data in applications:
        result.append({
            "id": app_data.id,
            "student_email": app_data.user.email,
            "father_name": app_data.father_name,
            "status": app_data.status
        })

    return jsonify(result), 200


from flask import current_app
from flask_mail import Message
from io import BytesIO
from reportlab.pdfgen import canvas

@app.route('/api/application/<int:app_id>', methods=['PUT'])
@jwt_required()
def update_application_status(app_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    if claims["role"] != "admin":
        return jsonify({"error": "Only admins can update application status"}), 403

    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["Approved", "Rejected"]:
        return jsonify({"error": "Status must be Approved or Rejected"}), 400

    application = StudentApplication.query.get(app_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    application.status = new_status
    db.session.commit()

    # If approved, generate and email offer letter
    if new_status == "Approved":
        # Generate PDF in memory
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, 800, "Offer Letter")

        c.setFont("Helvetica", 12)
        c.drawString(100, 750, f"Dear {application.user.name},")
        c.drawString(100, 730, "We are pleased to inform you that your application has been approved.")
        c.drawString(100, 710, "Congratulations and welcome aboard!")

        c.drawString(100, 680, f"Student Name : {application.user.name}")
        c.drawString(100, 660, f"Email        : {application.user.email}")
        c.drawString(100, 640, f"Phone        : {application.phone}")
        c.drawString(100, 620, f"Address      : {application.address}")

        c.drawString(100, 580, "Please keep this letter for your records.")
        c.drawString(100, 560, "Regards,")
        c.drawString(100, 540, "Admin Team")

        c.showPage()
        c.save()
        pdf_buffer.seek(0)

        # Send email with PDF attachment
        msg = Message(
            subject="Your Offer Letter",
            recipients=[application.user.email],
            body=f"Dear {application.user.name},\n\nPlease find attached your approved offer letter.\n\nBest regards,\nAdmin Team"
        )
        msg.attach(
            f"offer_letter_{application.user.name}.pdf",
            "application/pdf",
            pdf_buffer.read()
        )
        mail.send(msg)

    return jsonify({"message": f"Application {new_status}"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

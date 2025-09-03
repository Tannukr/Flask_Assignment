from flask import Flask, request, jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
import re
from flask_migrate import Migrate
from config import Config
from model import *
from student_route import register_offer_letter_routes
from flask import current_app
from flask_mail import Message
from io import BytesIO
from reportlab.pdfgen import canvas
from flask import send_file


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
mail = Mail(app)

migrate = Migrate(app, db)
app.config["JWT_SECRET_KEY"] = "your-secret-key"
jwt = JWTManager(app)


register_offer_letter_routes(app)



@app.route("/")
def home():
    return render_template("index.html")

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

    # Read form data
    father_name = request.form.get("father_name")
    mother_name = request.form.get("mother_name")
    phone = request.form.get("phone")
    address = request.form.get("address")
    tenth_year = request.form.get("tenth_year")
    tenth_marks = request.form.get("tenth_marks")
    twelfth_year = request.form.get("twelfth_year")
    twelfth_marks = request.form.get("twelfth_marks")

    # Handle file uploads
    degree_file = request.files.get("degree_certificate")
    id_file = request.files.get("id_file")

    if not degree_file or not id_file:
        return jsonify({"error": "Files are required"}), 400


    new_app = StudentApplication(
        user_id=current_user_id,
        father_name=father_name,
        mother_name=mother_name,
        phone=phone,
        address=address,
        tenth_year=tenth_year,
        tenth_marks=tenth_marks,
        twelfth_year=twelfth_year,
        twelfth_marks=twelfth_marks,
        degree_certificate_name = degree_file.filename,
        degree_certificate_data = degree_file.read(),
        id_proof_name = id_file.filename,
        id_proof_data = id_file.read(),
        status="Pending"
    )

    db.session.add(new_app)
    db.session.commit()

    return jsonify({
        "id": new_app.id,
        "status": new_app.status
    }), 201




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
            "student_name": app_data.user.name if app_data.user else None,
            "student_email": app_data.user.email if app_data.user else None,
            "father_name": app_data.father_name,
            "mother_name": app_data.mother_name,
            "phone": app_data.phone,
            "address": app_data.address,
            "tenth_year": app_data.tenth_year,
            "tenth_marks": app_data.tenth_marks,
            "twelfth_year": app_data.twelfth_year,
            "twelfth_marks": app_data.twelfth_marks,
            "degree_certificate_name": app_data.degree_certificate_name,
            "id_proof_name": app_data.id_proof_name,
            "status": app_data.status
        })

    return jsonify(result), 200




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


@app.route('/api/application/<int:app_id>/degree', methods=['GET'])
@jwt_required()
def download_degree_certificate(app_id):
    claims = get_jwt()
    if claims["role"] != "admin":
        return jsonify({"error": "Only admins can download documents"}), 403

    application = StudentApplication.query.get(app_id)
    if not application or not application.degree_certificate_data:
        return jsonify({"error": "Document not found"}), 404

    return send_file(
        BytesIO(application.degree_certificate_data),
        as_attachment=True,
        download_name=application.degree_certificate_name or "degree_certificate",
        mimetype="application/octet-stream"
    )


@app.route('/api/application/<int:app_id>/id-proof', methods=['GET'])
@jwt_required()
def download_id_proof(app_id):
    claims = get_jwt()
    if claims["role"] != "admin":
        return jsonify({"error": "Only admins can download documents"}), 403

    application = StudentApplication.query.get(app_id)
    if not application or not application.id_proof_data:
        return jsonify({"error": "Document not found"}), 404

    return send_file(
        BytesIO(application.id_proof_data),
        as_attachment=True,
        download_name=application.id_proof_name or "id_proof",
        mimetype="application/octet-stream"
    )

from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timezone

# Store revoked tokens
blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blacklist

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]   
    blacklist.add(jti)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/student-dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")


@app.route('/api/my-application', methods=['GET'])
@jwt_required()
def get_my_application():
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    if claims["role"] != "student":
        return jsonify({"error": "Only students can view this"}), 403

    application = StudentApplication.query.filter_by(user_id=current_user_id).first()
    if not application:
        return jsonify({"error": "No application found"}), 404

    return jsonify({
        "id": application.id,
        "status": application.status,
        "father_name": application.father_name,
        "mother_name": application.mother_name,
        "phone": application.phone,
        "address": application.address
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

# offer_letter.py
from flask import send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from io import BytesIO
from reportlab.pdfgen import canvas
from model import StudentApplication

def register_offer_letter_routes(app):
    @app.route('/api/offer-letter/<int:app_id>', methods=['GET'])
    @jwt_required()
    def download_offer_letter(app_id):
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        application = StudentApplication.query.get(app_id)
        if not application:
            return jsonify({"error": "Application not found"}), 404

        if claims["role"] == "student" and str(application.user_id) != str(current_user_id):
            return jsonify({"error": "You are not authorized to access this application"}), 403

        if application.status != "Approved":
            return jsonify({"error": "Offer letter available only for approved applications"}), 403

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

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"offer_letter_{application.user.name}.pdf",
            mimetype="application/pdf"
        )

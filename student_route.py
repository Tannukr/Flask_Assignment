from xhtml2pdf import pisa
from io import BytesIO
from flask import send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
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

        # One-page compact HTML template
        html = f"""
        <html>
        <head>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 12pt;
                    line-height: 1.5;
                }}
                h1 {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .content {{
                    margin-top: 20px;
                }}
                .info {{
                    margin-top: 20px;
                }}
                .footer {{
                    margin-top: 50px;
                }}
            </style>
        </head>
        <body>
            <h1>Offer Letter</h1>
            <div class="content">
                <p>Dear {application.user.name},</p>
                <p>
                    We are pleased to inform you that your application has been 
                    <b>approved</b>. Congratulations and welcome aboard!
                </p>
                <div class="info">
                    <p><b>Student Name:</b> {application.user.name}</p>
                    <p><b>Email:</b> {application.user.email}</p>
                    <p><b>Phone:</b> {application.phone}</p>
                    <p><b>Address:</b> {application.address}</p>
                </div>
                <div class="footer">
                    <p>Please keep this letter for your records.</p>
                    <p>Regards,<br>Admin Team</p>
                </div>
            </div>
        </body>
        </html>
        """

        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

        if pisa_status.err:
            return jsonify({"error": "Failed to generate PDF"}), 500

        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"offer_letter_{application.user.name}.pdf",
            mimetype="application/pdf"
        )

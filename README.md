# 🎓 Student Application Management API

A **Flask-based REST API** for managing student applications with authentication, database storage, PDF offer letters, and email notifications.

---

## 🚀 Features
- Student registration & login (**JWT auth**)
- Students submit applications
- Admin reviews applications (**approve/reject**)
- On **approval**, a **PDF offer letter** is generated and students can **download** it
- **`offer_letter.py`** route creates the PDF dynamically with student details
- Optional HTML page to preview/download the PDF in the browser
- Email notification to the student on approval (Gmail SMTP)
- Secure credentials via **`.env`**
- Postman collection included

---

## 🛠️ Setup

```bash
# Clone repository
git clone https://github.com/your-username/Flask_Assignement.git
cd Flask_Assignement

# Create virtual environment
python -m venv myenv
myenv\Scripts\activate   # Windows
source myenv/bin/activate # Mac/Linux

# Install dependencies
pip install -r requirements.txt

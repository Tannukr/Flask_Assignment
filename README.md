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

---

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=thisismysecretkey
MAIL_USERNAME="your-email@gmail.com"
MAIL_PASSWORD="your-app-password"

---

## ▶️ Running the App

```bash
flask run

---

Server will start at:  
👉 `http://127.0.0.1:5000`

---

## 📬 API Endpoints

| Method | Endpoint                  | Description                                |
|--------|---------------------------|--------------------------------------------|
| POST   | `/api/register`           | Register a new student                     |
| POST   | `/api/login`              | Login & receive JWT                        |
| POST   | `/api/application`        | Submit new application (student)           |
| GET    | `/api/applications`       | List all applications (admin only)         |
| PUT    | `/api/application/<id>`   | Update status (approve/reject) & send email|
| GET    | `/api/offer-letter/<id>`  | Download PDF offer letter (approved only)  |
| DELETE | `/api/student/<id>`       | Delete a student (admin only)              |

---

## 📄 Offer Letter

- Implemented in **`offer_letter.py`**  
- Uses **ReportLab** to dynamically generate PDF offer letters  
- Includes student details:
  - Name  
  - Email  
  - Phone  
  - Address  
- Available **only if the application is Approved**  
- Returns a downloadable PDF:  
  `offer_letter_<student>.pdf`

---

## 🧪 Testing with Postman

1. Import **`Flask_application.postman_collection.json`** into Postman  
2. Login with a registered student and get JWT token  
3. Use JWT token to test protected endpoints  
4. Submit, approve, and download offer letters  
5. Check **`students.db`** SQLite database for stored data  



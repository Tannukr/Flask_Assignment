# Student Application Management (Flask)

A Flask app with JWT auth where students submit applications and admins approve/reject them. Approved applications get a generated PDF offer letter that can be viewed in-browser and downloaded. Includes minimal UI pages for login, student dashboard, and admin dashboard.

---

## Features
- JWT-based auth: register, login, logout (token blacklist)
- Student application submission with file uploads
- Admin dashboard to approve/reject applications
- PDF offer letter generation (ReportLab), view and download from dashboard 
- Postman collection included

---

## Tech & Requirements
- Python 3.10+
- PostgreSQL (default URI in `config.py`)
  

---

## Setup

```bash
# 1) Clone and enter the project
git clone https://github.com/Tannukr/Flask_Assignment
cd Flask_Assignement

# 2) Create and activate a venv
python -m venv myenv
myenv\Scripts\activate   # Windows
# source myenv/bin/activate  # Mac/Linux

# 3) Install deps
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
SECRET_KEY=thisismysecretkey
DATABASE_URL=postgresql://postgres:1234@localhost:5432/Flask_database
# No mail configuration required anymore
```

Run the app:

```bash
flask run
# or: python app.py
```

App runs at `http://127.0.0.1:5000`.

---

## UI Pages
- `/` login/register page
  - On successful login, the response payload is:
    ```json
    {
      "message": "Login successful",
      "user": { "id": 1, "email": "...", "token": "<JWT>", "role": "admin|student" }
    }
    ```
  - The UI stores the token at `user.token`.

- `/student-dashboard`
  - If you already submitted an application, you see its status and can download the offer letter when Approved.
  - If not, you get a minimal application form (compact width) that posts a `multipart/form-data` payload with these keys:
    - `father_name`, `mother_name`, `phone`, `address`
    - `tenth_year`, `tenth_marks`, `twelfth_year`, `twelfth_marks`
    - `degree_certificate` (file), `id_proof` (file)

- `/admin-dashboard`
  - Lists all applications with full details and status.
  - For Pending, you can Approve/Reject. On approval, the student can view/download the offer letter.

---

## API Summary
- POST `/api/register` → Register a user (role: `student` or `admin`)
- POST `/api/login` → Returns `{ user: { id, email, token, role } }`
- POST `/api/application` (student, JWT)
  - Accepts form-data, requires files `degree_certificate` and `id_proof`
- GET `/api/my-application` (student, JWT)
- GET `/api/applications` (admin, JWT)
- PUT `/api/application/<id>` (admin, JWT) → Approve/Reject
- GET `/api/offer-letter/<id>` (JWT) → Returns PDF if Approved (suitable for view or download)
- POST `/api/logout` (JWT) → Blacklists the current token

---


---

## Postman
Import `Flask_application.postman_collection.json`, set the auth token variable to the JWT returned from login, and exercise the endpoints end-to-end.

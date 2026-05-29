# Axer Bank

A modern full-stack banking web application built using Python Flask, SQLite, HTML, CSS and JavaScript.

This project simulates a professional digital banking platform with authentication, analytics dashboards, transaction management and responsive UI design.

---

## Features

### Authentication

* User signup and login system
* Password validation and restrictions
* Secure password hashing
* Session-based authentication
* Logout functionality

### Dashboard

* Real-time account overview
* Balance cards
* Transaction history
* Analytics and charts
* Quick action buttons
* Responsive sidebar navigation

### Banking Features

* Transfer money page
* Transaction history
* Cards management UI
* Profile and settings pages
* Notifications UI
* Support/help center

### UI/UX

* Modern glassmorphism design
* Responsive layout
* Mobile-friendly dashboard
* Animated cards and buttons
* Interactive charts and analytics
* Clean reusable template structure

---

## Tech Stack

### Backend

* Python 3
* Flask
* SQLite

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

---

## Project Structure

```bash
Axer-Bank/
│
├── app.py
├── auth.py
├── db.py
├── requirements.txt
├── .gitignore
│
├── instance/
│   └── banking.sqlite3
│
├── static/
│   ├── styles.css
│   └── js/
│
├── templates/
│   ├── layouts/
│   ├── partials/
│   └── pages/
│
└── venv/
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/axer-bank.git
```

### Move Into Project

```bash
cd axer-bank
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Mac/Linux

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run The Application

```bash
python app.py
```

Open browser:

```bash
http://127.0.0.1:5000
```

---

## Security Features

* Password hashing using Werkzeug
* Input validation
* Session protection
* Secure authentication flow
* Form validation rules
* Protected dashboard routes

---

## Future Improvements

* Real banking APIs
* Email verification
* OTP authentication
* Admin dashboard
* Dark/light mode
* Budget planner
* AI financial assistant
* Real payment gateway integration

---

## Screenshots

Add screenshots of:

* Homepage
* Dashboard
* Analytics
* Login page
* Transfer page

---

## Learning Goals

This project was built to learn:

* Flask backend development
* Authentication systems
* SQLite databases
* Frontend/backend integration
* Responsive UI design
* Project structuring
* Full-stack web development

---

## Disclaimer

This is a demo educational banking application and is not intended for real financial transactions.

---

## Author

Developed by Deepak Gulani

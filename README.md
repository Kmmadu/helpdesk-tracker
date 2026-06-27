# 🛠 Helpdesk Ticketing Tracker

A full-stack IT support ticket management system built to simulate a real Service Desk workflow.

This project demonstrates practical IT support concepts including:

- Incident reporting
- Ticket assignment
- Troubleshooting documentation
- Resolution tracking
- Knowledge management
- Support analytics


## 📸 Project Screenshot

![Helpdesk Dashboard Screenshot](./screenshots/dashboard.png)


## 🚀 Features

### Ticket Management

- Create and manage support tickets
- Assign tickets to technicians
- Track ticket priority and status
- Filter tickets by category, priority, and status


### Ticket Activity Timeline

Every ticket keeps a history of actions:

Example:

- Ticket created
- Assigned to technician
- Status changed
- Troubleshooting notes added
- Ticket resolved

---


### Troubleshooting Documentation

Technicians can document:

- Root cause
- Steps performed
- Resolution summary
- Prevention notes


### Knowledge Base

Resolved issues can be converted into reusable knowledge articles.

Examples:

- WiFi connectivity issues
- Password reset procedures
- Printer troubleshooting
- Network access problems


### Dashboard Analytics

The dashboard displays:

- Total tickets
- Open tickets
- Resolved tickets
- Critical issues
- Common ticket categories


---

# 🏗 Architecture

```bash
helpdesk-tracker/

backend/
FastAPI REST API
SQLite Database
SQLAlchemy ORM

frontend/
HTML
CSS
Vanilla JavaScript
```



---

# 🧰 Tech Stack

## Backend

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic


## Frontend

- HTML5
- CSS3
- JavaScript


---

# 📂 Project Structure

```bash
helpdesk-tracker/

├── backend/
│
├── frontend/
│
└── README.md
```


---

# ⚙️ Installation


## Backend Setup


Navigate into backend:


```bash
cd backend
Create virtual environment:
python -m venv venv
- Activate:

- Windows:
venv\Scripts\activate

- Linux/Mac:
source venv/bin/activate

- Install dependencies:
pip install -r requirements.txt

- Run server:
python run.py

- API available at:
http://localhost:8000
```

---

## Frontend Setup

Open:

```bash
frontend/index.html
```

# 🎯 Project Purpose

This project was created as a portfolio demonstration for IT Support / Network Engineering roles.

The goal is to demonstrate understanding of:

- IT service workflows
- Incident management
- Troubleshooting processes
- Documentation practices
- Backend API development

---

## 👨🏽‍💻 Author

Kingsley

IT Support Engineer | Networking | Cybersecurity

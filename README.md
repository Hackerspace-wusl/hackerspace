# 🚀 Hackerspace Management System

A robust, modern platform for managing community news, projects, and members. Built with Flask and a hybrid database architecture (MongoDB + SQLite/PostgreSQL), Hackerspace provides a structured way to share content, manage members, and collaborate on innovative projects.

![Hackerspace](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)

---

## ✨ Key Features

- **🔐 Secure Authentication**: Multi-layered auth system using Flask-Login and MongoDB.
- **📰 News & Articles**: Create rich articles with a structured block-based content system.
- **🛠 Project Showcase**: Gallery for community projects with detailed descriptions and media support.
- **👥 Member Management**: Directory of community members with profile customization.
- **🛡️ Role-Based Access**: Granular permissions for Users, Authors, and Super Admins.
- **✍️ Rich Text Editing**: Integrated CKEditor for seamless content creation.
- **📁 Media Support**: Built-in file upload handling for article and project media.
- **📱 Responsive Design**: Clean UI that works across all devices.

---

## 🛠 Tech Stack

- **Backend**: Flask (Python)
- **Database**:
  - **MongoDB**: For User Auth and Profile data.
  - **SQLAlchemy (SQLite/PostgreSQL)**: For Articles, Projects, and Reminders.
- **Frontend**: Jinja2 Templates, Vanilla CSS, JavaScript.
- **Security**: Flask-Bcrypt for password hashing.
- **Environment**: Python-Dotenv for sensitive configuration.

---

## 🚀 Getting Started (Local Deployment)

Follow these steps to set up the project on your local machine.

### 1. Prerequisites
- Python 3.8 or higher installed.
- A MongoDB Atlas account (or local MongoDB).
- Git installed.

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/hackerspace.git
cd hackerspace
```

### 3. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file in the root directory and add the following:
```env
SECRET_KEY=your_very_secret_key_here
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/hackerspace_auth?retryWrites=true&w=majority
DATABASE_URL=sqlite:///hackerspace.db
```

### 6. Run the Application
```bash
python app.py
```
The app will be available at `http://localhost:5000`.

---

## 🔧 Environment Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | None (Required) |
| `MONGO_URI` | MongoDB connection string | None (Required) |
| `DATABASE_URL` | SQLAlchemy database URI | `sqlite:///hackerspace.db` |

---

## 🤝 Contributing

We welcome contributions! To contribute:

1. **Fork** the repository.
2. **Create a branch** for your feature: `git checkout -b feature/amazing-feature`.
3. **Commit** your changes: `git commit -m 'Add some amazing feature'`.
4. **Push** to the branch: `git push origin feature/amazing-feature`.
5. **Open a Pull Request**.

Please ensure your code follows the PEP 8 guidelines and includes proper comments.

---

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

<p align="center">Made with ❤️ by the Hackerspace-wusl Team</p>

# 🚀 Hackerspace Management System

A robust, modern platform for managing community news, projects, and members. Built with Flask and a hybrid database architecture (**MongoDB** + **PostgreSQL**), Hackerspace provides a structured way to share content, manage members, and collaborate on innovative projects.

![Hackerspace](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)
![Vercel](https://img.shields.io/badge/Deploy-Vercel-black)

---

## ✨ Key Features

- **🔐 Secure Authentication**: Multi-layered auth system using Flask-Login and MongoDB.
- **📰 News & Articles**: Create rich articles with a modular block-based content system (CKEditor integrated).
- **🛠 Project Showcase**: Gallery for community projects with detailed descriptions and media support.
- **👥 Member Management**: Directory of community members with profile customization and role-based access.
- **🛡️ Role-Based Access**: Granular permissions for **Users**, **Authors**, and **Super Admins**.
- **⚡ Vercel Ready**: Pre-configured for serverless deployment with `vercel.json`.
- **📁 Hybrid Storage**: Optimized for both NoSQL (Auth) and Relational (Content) needs.

---

## 🛠 Tech Stack

- **Backend**: Flask (Python)
- **Database**:
  - **MongoDB Atlas**: For User Authentication and Profile data.
  - **PostgreSQL**: For Articles, Projects, and Reminders (Neon.tech recommended).
- **Frontend**: Jinja2 Templates, Vanilla CSS, JavaScript.
- **Security**: Flask-Bcrypt for password hashing.
- **Hosting**: Optimized for **Vercel** serverless functions.

---

## 🚀 Getting Started (Local Deployment)

### 1. Prerequisites
- Python 3.8 or higher installed.
- MongoDB Atlas account.
- PostgreSQL database (or Neon.tech account).

### 2. Setup
```bash
git clone https://github.com/yourusername/hackerspace.git
cd hackerspace
python -m venv venv
# Windows: venv\Scripts\activate | Unix: source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your_very_secret_key
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/hackerspace_auth
DATABASE_URL=postgresql://<user>:<password>@<host>/neondb?sslmode=require
```

### 4. Run
```bash
python app.py
```
Visit `http://localhost:5000` to see your app.

---

## ☁️ Deployment (Vercel)

The project is pre-configured for Vercel deployment.

1. **Install Vercel CLI**: `npm i -g vercel`
2. **Deploy**: Run `vercel` in the project root.
3. **Configure**: Add the variables from your `.env` to the **Vercel Dashboard** under Project Settings.

> [!IMPORTANT]
> **Storage Note**: Since Vercel is serverless, files uploaded via the editor are ephemeral and will be lost after a restart. For production persistence, integrate an external storage provider like Cloudinary or AWS S3.

---

## 🔧 Environment Configuration

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key for sessions |
| `MONGO_URI` | MongoDB connection string (Atlas) |
| `DATABASE_URL` | PostgreSQL connection string |

---

## 🤝 Contributing

1. **Fork** the repository.
2. **Create a branch**: `git checkout -b feature/amazing-feature`.
3. **Commit** changes: `git commit -m 'Add some amazing feature'`.
4. **Push**: `git push origin feature/amazing-feature`.
5. **Open a Pull Request**.

---

<p align="center">Made with ❤️ by the Hackerspace Team</p>

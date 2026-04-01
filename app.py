from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import json

from extensions import db, bcrypt, login_manager
from models import User, Project, Article, Reminder, Member, ContentBlock
from database import init_mongodb, get_users_col
from bson import ObjectId

load_dotenv()

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# Initialize MongoDB
init_mongodb(app)

with app.app_context():
    db.create_all()


def get_user_by_id(user_id):
    try:
        return {"_id": int(user_id)}
    except (ValueError, TypeError):
        return {"_id": ObjectId(user_id)}


# Redundant function, keeping it if needed for legacy reasons or removing if not used
def get_user_query(user_id):
    return get_user_by_id(user_id)


def check_content_permission(item, user):
    if not item:
        return False
    if user.is_admin:
        return True
    return str(item.author_id) == str(user.id)


@login_manager.user_loader
def load_user(user_id):
    try:
        query = get_user_by_id(user_id)
        user_data = get_users_col().find_one(query)
        if user_data:
            print(f"User loaded: {user_data.get('email')}")
            return User(user_data=user_data)
        print(f"User loading failed for ID: {user_id}")
        return None
    except Exception as e:
        print(f"Error loading user: {e}")
        return None


# --- Auth Routes ---
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        if get_users_col().find_one({"email": email}):
            flash("Email already exists")
            return redirect(url_for("signup"))

        try:
            role = "user"
            max_user = get_users_col().find_one(sort=[("_id", -1)])
            next_id = (max_user.get("_id", 0) + 1) if max_user else 1

            hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
            get_users_col().insert_one(
                {
                    "_id": next_id,
                    "username": username,
                    "email": email,
                    "password": hashed_pw,
                    "role": role,
                }
            )
            flash("Signup successful! Please login.")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Signup error: {e}")
            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        print(f"User {current_user.email} already authenticated. Redirect.")
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        print(f"Login attempt for: {email}")

        try:
            user_data = get_users_col().find_one({"email": email})
            if user_data:
                print(f"User found in DB: {email}")
                if bcrypt.check_password_hash(user_data["password"], password):
                    login_user(User(user_data))
                    print(f"Login successful for {email}")
                    next_page = request.args.get("next")
                    if not next_page or not next_page.startswith("/") or next_page.startswith("//"):
                        next_page = url_for("index")
                    return redirect(next_page)
                else:
                    print(f"Invalid password for {email}")
                    flash("Invalid password")
            else:
                print(f"Email not found: {email}")
                flash("Email not found")
        except Exception as e:
            msg = (
                "MongoDB Error: Could not connect to database. "
                "Please check your Atlas IP whitelist."
            )
            flash(msg)
            print(f"Login error: {e}")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        avatar = request.form.get("avatar")
        password = request.form.get("password")

        update_data = {"username": username, "email": email, "avatar": avatar}

        if password:
            hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
            update_data["password"] = hashed_pw

        # Check email uniqueness
        if email.strip().lower() != current_user.email:
            if get_users_col().find_one({"email": email.strip().lower()}):
                flash("Email already in use by another account.")
                return redirect(url_for("edit_profile"))

        try:
            get_users_col().update_one(
                get_user_by_id(current_user.id), {"$set": update_data}
            )
            flash("Profile updated successfully!")
            return redirect(url_for("edit_profile"))
        except Exception as e:
            flash(f"Error updating profile: {e}")

    return render_template("edit_profile.html")


# --- Main Routes ---
@app.route("/")
def index():
    if not current_user.is_authenticated:
        return render_template("guest.html")
    return render_template("index.html")


@app.route("/news")
@login_required
def news():
    return render_template("news.html")


@app.route("/make-admin")
@login_required
def make_admin():
    # Security: Only allow self-promotion if no super admins exist
    if get_users_col().count_documents({"role": "super_admin"}) > 0:
        flash("Action denied. A super admin already exists.")
        return redirect(url_for("index"))

    try:
        get_users_col().update_one(
            get_user_by_id(current_user.id), {"$set": {"role": "super_admin"}}
        )
        current_user.role = "super_admin"
        flash("Success! Your account has been upgraded to super admin.")
    except Exception as e:
        flash(f"Error upgrading account: {e}")
    return redirect(url_for("index"))


@app.route("/create-article", methods=["GET", "POST"])
@login_required
def create_article():
    if not current_user.is_author:
        flash("Permission denied. Only authors can access this page.")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title")
        content_type = request.form.get("content_type")
        blocks_data_str = request.form.get("blocks_data")

        try:
            blocks = json.loads(blocks_data_str)

            # Handle file uploads for each block
            for block in blocks:
                has_file = block.get("file_key") in request.files
                if block.get("file_key") and has_file:
                    file = request.files[block["file_key"]]
                    if file and file.filename:
                        safe_name = secure_filename(file.filename)
                        filename = f"{ObjectId()}_{safe_name}"
                        save_path = os.path.join(
                            "static", "uploads", "content", filename
                        )
                        full_path = os.path.join(app.root_path, save_path)
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        file.save(full_path)
                        block["value"] = "/" + save_path.replace("\\", "/")

            if content_type == "news":
                new_item = Article(
                    title=title, author=current_user.username, author_id=current_user.id
                )
            else:
                new_item = Project(
                    title=title, color="#fdfaf6", author_id=current_user.id
                )

            db.session.add(new_item)
            db.session.flush()  # Get the ID for foreign keys

            # Create structured blocks
            for i, block_data in enumerate(blocks):
                new_block = ContentBlock(
                    article_id=new_item.id if content_type == "news" else None,
                    project_id=new_item.id if content_type != "news" else None,
                    type=block_data["type"],
                    sub_type=block_data["sub_type"],
                    value=block_data.get("value", ""),
                    sequence=i,
                )
                db.session.add(new_block)

            db.session.commit()

            target_page = "news" if content_type == "news" else "index"
            is_news = content_type == "news"
            msg = f'{"Article" if is_news else "Project"} published!'
            flash(msg)
            return redirect(url_for(target_page))

        except Exception as e:
            db.session.rollback()
            print(f"Error publishing: {e}")
            flash(f"Error publishing content: {e}")

    return render_template("create_article.html")


@app.route("/members")
@login_required
def members():
    return render_template("members.html")


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


@app.route("/manage-content")
@login_required
def manage_content():
    if not current_user.is_author and not current_user.is_admin:
        flash("Permission denied.")
        return redirect(url_for("index"))

    # Authors see their own, Admins see everything
    if current_user.is_admin:
        articles = Article.query.all()
        projects = Project.query.all()
    else:
        articles = Article.query.filter_by(author_id=current_user.id).all()
        projects = Project.query.filter_by(author_id=current_user.id).all()

    return render_template("manage_content.html", articles=articles, projects=projects)


@app.route("/edit-content/<type>/<int:id>", methods=["GET", "POST"])
@login_required
def edit_content(type, id):
    type = type.lower()
    if type == "news":
        item = db.session.get(Article, id)
    else:
        item = db.session.get(Project, id)

    if not check_content_permission(item, current_user):
        flash("Item not found or permission denied.")
        return redirect(url_for("manage_content"))

    if request.method == "POST":
        title = request.form.get("title")
        blocks_data_str = request.form.get("blocks_data")

        try:
            blocks = json.loads(blocks_data_str)
            for block in blocks:
                has_file = block.get("file_key") in request.files
                if block.get("file_key") and has_file:
                    file = request.files[block["file_key"]]
                    if file and file.filename:
                        safe_name = secure_filename(file.filename)
                        filename = f"{ObjectId()}_{safe_name}"
                        save_path = os.path.join(
                            "static", "uploads", "content", filename
                        )
                        full_path = os.path.join(app.root_path, save_path)
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        file.save(full_path)
                        block["value"] = "/" + save_path.replace("\\", "/")

            item.title = title

            # Clear existing blocks and recreate
            ContentBlock.query.filter_by(
                article_id=item.id if type == "news" else None,
                project_id=item.id if type != "news" else None,
            ).delete()

            for i, block_data in enumerate(blocks):
                new_block = ContentBlock(
                    article_id=item.id if type == "news" else None,
                    project_id=item.id if type != "news" else None,
                    type=block_data["type"],
                    sub_type=block_data["sub_type"],
                    value=block_data.get("value", ""),
                    sequence=i,
                )
                db.session.add(new_block)

            db.session.commit()
            flash("Content updated successfully!")
            return redirect(url_for("manage_content"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating content: {e}")

    # Pass existing blocks as JSON list for the frontend editor
    blocks_list = [b.to_dict() for b in item.blocks]
    return render_template(
        "create_article.html",
        item=item,
        content_type=type,
        existing_blocks=json.dumps(blocks_list),
    )


@app.route("/toggle-visibility/<type>/<int:id>")
@login_required
def toggle_visibility(type, id):
    type = type.lower()
    if type == "news":
        item = db.session.get(Article, id)
    else:
        item = db.session.get(Project, id)

    if not check_content_permission(item, current_user):
        flash("Item not found or permission denied.")
        return redirect(url_for("manage_content"))

    item.is_private = not item.is_private
    db.session.commit()
    flash("Visibility updated.")
    return redirect(url_for("manage_content"))


@app.route("/delete-content/<type>/<int:id>")
@login_required
def delete_content(type, id):
    type = type.lower()
    if type == "news":
        item = db.session.get(Article, id)
    else:
        item = db.session.get(Project, id)

    if not check_content_permission(item, current_user):
        flash("Item not found or permission denied.")
        return redirect(url_for("manage_content"))

    db.session.delete(item)
    db.session.commit()
    flash("Item deleted successfully.")
    return redirect(url_for("manage_content"))


# --- API Routes ---
@app.route("/api/projects")
def api_projects():
    projects = Project.query.filter_by(is_private=False).all()
    return jsonify([p.to_dict() for p in projects])


@app.route("/api/articles")
def api_articles():
    articles = Article.query.filter_by(is_private=False).all()
    return jsonify([a.to_dict() for a in articles])


@app.route("/api/reminders")
@login_required
def api_reminders():
    reminders = Reminder.query.all()
    return jsonify([r.to_dict() for r in reminders])


@app.route("/api/members")
@login_required
def api_members():
    members = Member.query.all()
    return jsonify([m.to_dict() for m in members])


@app.route("/admin/users", methods=["GET", "POST"])
@login_required
def manage_users():
    if not current_user.is_admin:
        flash("Access denied. Admin only.")
        return redirect(url_for("index"))

    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_role = request.form.get("role")

        try:
            get_users_col().update_one(
                get_user_query(user_id), {"$set": {"role": new_role}}
            )
            flash("User role updated successfully!")
        except Exception as e:
            flash(f"Error updating role: {e}")
        return redirect(url_for("manage_users"))

    # Exclude password hashes from the query for security
    users = list(get_users_col().find({}, {"password": 0}))
    return render_template("manage_users.html", users=users)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

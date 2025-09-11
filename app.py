from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'qwertyuiopasdfghjkl'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/leetflix'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------
# ✅ DATABASE TABLES
# ---------------------------
class Users(db.Model):
    __tablename__ = 'users'
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

class Login(db.Model):
    __tablename__ = 'login'
    sno = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    dateTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    options = db.relationship('Option', backref='question', lazy=True)

class Option(db.Model):
    __tablename__ = 'options'
    option_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

# ---------------------------
# 🔹 HOME PAGE
# ---------------------------
@app.route("/")
def home():
    return render_template('trivia.html')

# ---------------------------
# 🔹 LOGIN ROUTE
# ---------------------------
@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Users.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            log_entry = Login(email=email)
            db.session.add(log_entry)
            db.session.commit()

            session['user'] = user.name
            flash("✅ Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("❌ Invalid email or password!", "danger")
            return redirect(url_for('login_page'))

    return render_template('login.html')

# ---------------------------
# 🔹 LOGOUT
# ---------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# ---------------------------
# 🔹 REGISTER ROUTE
# ---------------------------
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash("⚠️ User already exists. Please log in.", "warning")
            return redirect(url_for('login_page'))

        # Explicit method for hashing (important!)
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = Users(name=name, email=email, password=hashed_pw)

        db.session.add(new_user)
        db.session.commit()

        flash("✅ Registration successful! Please log in.", "success")
        return redirect(url_for('login_page'))

    return render_template('register.html')

# ---------------------------
# 🔹 QUIZ ROUTE
# ---------------------------
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "q_index" not in session:
        session["q_index"] = 0
        session["score"] = 0

    total_questions = Question.query.count()

    if request.method == "POST":
        selected_option_id = request.form.get("option")

        if selected_option_id:
            try:
                selected_option_id = int(selected_option_id)
                option = Option.query.filter_by(option_id=selected_option_id).first()
                if option and option.is_correct:
                    session["score"] += 1
                    flash("✅ Correct!", "success")
                else:
                    flash("❌ Wrong!", "danger")
            except ValueError:
                flash("⚠️ Invalid selection.", "warning")

        session["q_index"] += 1

        if session["q_index"] >= total_questions:
            score = session["score"]
            session.pop("q_index")
            session.pop("score")
            return redirect(url_for("quiz_result", score=score, total=total_questions))

    question = Question.query.offset(session["q_index"]).first()
    if not question:
        flash("⚠️ No questions available.", "warning")
        return redirect(url_for("home"))

    return render_template("quiz.html", question=question)

# ---------------------------
# 🔹 QUIZ RESULT
# ---------------------------
@app.route("/quiz_result")
def quiz_result():
    score = request.args.get("score", 0, type=int)
    total = request.args.get("total", 0, type=int)
    return render_template("result.html", score=score, total=total)

# ---------------------------
# 🔹 RUN APP
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)

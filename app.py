# # from flask import Flask, render_template, request, redirect, url_for, flash, session
# # from flask_sqlalchemy import SQLAlchemy
# # from datetime import datetime
# # from werkzeug.security import generate_password_hash, check_password_hash

# # app = Flask(__name__)
# # app.secret_key = 'qwertyuiopasdfghjkl'
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/leetflix'
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # db = SQLAlchemy(app)

# # # ---------------------------
# # # ✅ DATABASE TABLES (UPDATED)
# # # ---------------------------
# # class Users(db.Model):
# #     __tablename__ = 'users'
# #     sno = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(100), nullable=False)
# #     email = db.Column(db.String(50), nullable=False, unique=True)
# #     password = db.Column(db.String(255), nullable=False)

# # class Login(db.Model):
# #     __tablename__ = 'login'
# #     sno = db.Column(db.Integer, primary_key=True)
# #     email = db.Column(db.String(50), nullable=False)
# #     dateTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# # class Question(db.Model):
# #     __tablename__ = 'questions'
# #     question_id = db.Column(db.Integer, primary_key=True)
# #     text = db.Column(db.String(255), nullable=False)
# #     # Added show_name and season to the model
# #     show_name = db.Column(db.String(255), nullable=False)
# #     season = db.Column(db.Integer, nullable=False)
# #     options = db.relationship('Option', backref='question', lazy=True)

# # class Option(db.Model):
# #     __tablename__ = 'options'
# #     option_id = db.Column(db.Integer, primary_key=True)
# #     question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
# #     text = db.Column(db.String(255), nullable=False)
# #     is_correct = db.Column(db.Boolean, default=False)

# # # ---------------------------
# # # 🔹 HOME PAGE
# # # ---------------------------
# # @app.route("/")
# # def home():
# #     return render_template('trivia.html')

# # # ---------------------------
# # # 🔹 SEASONS PAGE (NEW)
# # # ---------------------------
# # @app.route("/seasons/<show_name>")
# # def seasons_page(show_name):
# #     # This new route renders the seasons page for the selected show.
# #     return render_template('seasons.html', show_name=show_name)

# # # ---------------------------
# # # 🔹 LOGIN ROUTE
# # # ---------------------------
# # @app.route("/login", methods=['GET', 'POST'])
# # def login_page():
# #     if request.method == 'POST':
# #         email = request.form.get('email')
# #         password = request.form.get('password')

# #         user = Users.query.filter_by(email=email).first()

# #         if user and check_password_hash(user.password, password):
# #             log_entry = Login(email=email)
# #             db.session.add(log_entry)
# #             db.session.commit()

# #             # --- CHANGE HERE ---
# #             # Store the part of the email before the '@' as the user's name
# #             session['user'] = user.email.split('@')[0]
            
# #             flash("✅ Login successful!", "success")
# #             return redirect(url_for('home'))
# #         else:
# #             flash("❌ Invalid email or password!", "danger")
# #     return render_template('login.html')

# # # ---------------------------
# # # 🔹 LOGOUT
# # # ---------------------------
# # @app.route('/logout')
# # def logout():
# #     session.pop('user', None)
# #     flash("You have been logged out.", "info")
# #     return redirect(url_for('home'))

# # # ---------------------------
# # # 🔹 REGISTER ROUTE
# # # ---------------------------
# # @app.route("/register", methods=['GET', 'POST'])
# # def register():
# #     if request.method == 'POST':
# #         name = request.form.get('name')
# #         email = request.form.get('email')
# #         password = request.form.get('password')
# #         existing_user = Users.query.filter_by(email=email).first()
# #         if existing_user:
# #             flash("⚠️ User already exists. Please log in.", "warning")
# #             return redirect(url_for('login_page'))
# #         hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
# #         new_user = Users(name=name, email=email, password=hashed_pw)
# #         db.session.add(new_user)
# #         db.session.commit()
# #         flash("✅ Registration successful! Please log in.", "success")
# #         return redirect(url_for('login_page'))
# #     return render_template('register.html')

# # # ---------------------------
# # # 🔹 QUIZ ROUTE (UPDATED LOGIC)
# # # ---------------------------
# # @app.route("/quiz", methods=["GET", "POST"])
# # def quiz():
# #     # If a new quiz is starting (from seasons.html), set it up in the session
# #     if request.method == "GET":
# #         show_name = request.args.get('show')
# #         season = request.args.get('season', type=int)
        
# #         if show_name and season:
# #             session.clear() # Clear any old quiz data
# #             questions_for_quiz = Question.query.filter_by(show_name=show_name, season=season).all()
# #             if not questions_for_quiz:
# #                 flash(f"⚠️ No questions found for {show_name} Season {season}.", "warning")
# #                 return redirect(url_for("home"))
            
# #             # Store the list of question IDs for this specific quiz
# #             session['question_ids'] = [q.question_id for q in questions_for_quiz]
# #             session['q_index'] = 0
# #             session['score'] = 0
# #             session['total_questions'] = len(session['question_ids'])
# #             session['show_name'] = show_name # Store for display
    
# #     # Check if a quiz is actually in progress
# #     if 'question_ids' not in session:
# #         flash("⚠️ Please select a quiz to start.", "warning")
# #         return redirect(url_for("home"))

# #     total_questions = session.get('total_questions', 0)

# #     # Handle the form submission for the current question
# #     if request.method == "POST":
# #         selected_option_id = request.form.get("option")
# #         if selected_option_id:
# #             try:
# #                 option = Option.query.get(int(selected_option_id))
# #                 if option and option.is_correct:
# #                     session["score"] += 1
# #                     flash("✅ Correct!", "success")
# #                 else:
# #                     flash("❌ Wrong!", "danger")
# #             except (ValueError, TypeError):
# #                 flash("⚠️ Invalid selection.", "warning")
        
# #         session["q_index"] += 1

# #     q_index = session.get("q_index", 0)

# #     # Check if the quiz is over
# #     if q_index >= total_questions:
# #         score = session.get("score", 0)
# #         session.clear() # Clear all quiz data
# #         return redirect(url_for("quiz_result", score=score, total=total_questions))

# #     # Fetch the next question based on the ID from our session list
# #     current_question_id = session['question_ids'][q_index]
# #     question = Question.query.get(current_question_id)
# #     show_name_for_title = session.get('show_name', 'Trivia')

# #     if not question:
# #         flash("⚠️ A question could not be loaded. Please try again.", "warning")
# #         session.clear()
# #         return redirect(url_for("home"))

# #     return render_template("quiz.html", question=question, show_name=show_name_for_title)

# # # ---------------------------
# # # 🔹 QUIZ RESULT
# # # ---------------------------
# # @app.route("/quiz_result")
# # def quiz_result():
# #     score = request.args.get("score", 0, type=int)
# #     total = request.args.get("total", 0, type=int)
# #     return render_template("result.html", score=score, total=total)

# # # ---------------------------
# # # 🔹 RUN APP
# # # ---------------------------
# # if __name__ == '__main__':
# #     app.run(debug=True)

# from flask import Flask, render_template, request, redirect, url_for, flash, session
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash

# app = Flask(__name__)
# app.secret_key = 'qwertyuiopasdfghjkl'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/leetflix'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# # ---------------------------
# # ✅ DATABASE TABLES
# # ---------------------------
# class Users(db.Model):
#     __tablename__ = 'users'
#     sno = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(50), nullable=False, unique=True)
#     password = db.Column(db.String(255), nullable=False)
#     # Relationship to QuizResult
#     results = db.relationship('QuizResult', backref='user', lazy=True)

# class Login(db.Model):
#     __tablename__ = 'login'
#     sno = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(50), nullable=False)
#     dateTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# class Question(db.Model):
#     __tablename__ = 'questions'
#     question_id = db.Column(db.Integer, primary_key=True)
#     text = db.Column(db.String(255), nullable=False)
#     show_name = db.Column(db.String(255), nullable=False)
#     season = db.Column(db.Integer, nullable=False)
#     options = db.relationship('Option', backref='question', lazy=True)

# class Option(db.Model):
#     __tablename__ = 'options'
#     option_id = db.Column(db.Integer, primary_key=True)
#     question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
#     text = db.Column(db.String(255), nullable=False)
#     is_correct = db.Column(db.Boolean, default=False)

# # --- NEW TABLE FOR SCORES ---
# class QuizResult(db.Model):
#     __tablename__ = 'quiz_results'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.sno'), nullable=False)
#     show_name = db.Column(db.String(100), nullable=False)
#     season = db.Column(db.Integer, nullable=False)
#     score = db.Column(db.Integer, nullable=False)
#     total_questions = db.Column(db.Integer, nullable=False)
#     date_taken = db.Column(db.DateTime, default=datetime.utcnow)

# # ---------------------------
# # 🔹 HOME & SEASONS PAGES
# # ---------------------------
# @app.route("/")
# def home():
#     return render_template('trivia.html')

# @app.route("/seasons/<show_name>")
# def seasons_page(show_name):
#     return render_template('seasons.html', show_name=show_name)

# # ---------------------------
# # 🔹 LOGIN / LOGOUT / REGISTER
# # ---------------------------
# @app.route("/login", methods=['GET', 'POST'])
# def login_page():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#         user = Users.query.filter_by(email=email).first()

#         if user and check_password_hash(user.password, password):
#             log_entry = Login(email=email)
#             db.session.add(log_entry)
#             db.session.commit()
            
#             # --- UPDATED SESSION ---
#             session['user'] = user.email.split('@')[0]
#             session['user_id'] = user.sno # Store user's ID
            
#             flash("✅ Login successful!", "success")
#             return redirect(url_for('home'))
#         else:
#             flash("❌ Invalid email or password!", "danger")
#             return redirect(url_for('login_page'))
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear() # Clears the entire session
#     flash("You have been logged out.", "info")
#     return redirect(url_for('home'))

# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         existing_user = Users.query.filter_by(email=email).first()
#         if existing_user:
#             flash("⚠️ User already exists. Please log in.", "warning")
#             return redirect(url_for('login_page'))
#         hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
#         new_user = Users(name=name, email=email, password=hashed_pw)
#         db.session.add(new_user)
#         db.session.commit()
#         flash("✅ Registration successful! Please log in.", "success")
#         return redirect(url_for('login_page'))
#     return render_template('register.html')

# # ---------------------------
# # 🔹 QUIZ LOGIC (UPDATED)
# # ---------------------------
# @app.route("/quiz", methods=["GET", "POST"])
# def quiz():
#     if request.method == "GET":
#         show_name = request.args.get('show')
#         season = request.args.get('season', type=int)
#         if show_name and season:
#             # Starting a new quiz
#             questions_for_quiz = Question.query.filter_by(show_name=show_name, season=season).all()
#             if not questions_for_quiz:
#                 flash(f"⚠️ No questions found for {show_name} Season {season}.", "warning")
#                 return redirect(url_for("home"))
#             # Store all quiz info in session
#             session['question_ids'] = [q.question_id for q in questions_for_quiz]
#             session['q_index'] = 0
#             session['score'] = 0
#             session['show_name'] = show_name
#             session['season'] = season
#             session['total_questions'] = len(session['question_ids'])
    
#     if "q_index" not in session or 'question_ids' not in session:
#         flash("⚠️ Please select a quiz to start.", "warning")
#         return redirect(url_for("home"))

#     if request.method == "POST":
#         selected_option_id = request.form.get("option")
#         if selected_option_id:
#             try:
#                 option = Option.query.get(int(selected_option_id))
#                 if option and option.is_correct:
#                     session["score"] += 1
#                     flash("✅ Correct!", "success")
#                 else:
#                     flash("❌ Wrong!", "danger")
#             except (ValueError, TypeError):
#                 flash("⚠️ Invalid selection.", "warning")
#         session["q_index"] += 1

#     q_index = session.get("q_index", 0)
#     total_questions = session.get('total_questions', 0)
    
#     if q_index >= total_questions:
#         score = session.get("score", 0)
#         return redirect(url_for("quiz_result", score=score, total=total_questions))

#     current_question_id = session['question_ids'][q_index]
#     question = Question.query.get(current_question_id)
#     return render_template("quiz.html", question=question)

# # ---------------------------
# # 🔹 QUIZ RESULT (UPDATED)
# # ---------------------------
# @app.route("/quiz_result")
# def quiz_result():
#     score = request.args.get("score", 0, type=int)
#     total = request.args.get("total", 0, type=int)

#     # --- SAVE SCORE TO DB ---
#     if 'user_id' in session:
#         user_id = session['user_id']
#         show_name = session.get('show_name')
#         season = session.get('season')
        
#         if show_name and season:
#             new_result = QuizResult(
#                 user_id=user_id,
#                 show_name=show_name,
#                 season=season,
#                 score=score,
#                 total_questions=total
#             )
#             db.session.add(new_result)
#             db.session.commit()

#     # Clear quiz-specific session data
#     session.pop('question_ids', None)
#     session.pop('q_index', None)
#     session.pop('score', None)
#     session.pop('show_name', None)
#     session.pop('season', None)
#     session.pop('total_questions', None)
    
#     return render_template("result.html", score=score, total=total)

# # ---------------------------
# # 🔹 PROFILE PAGE (NEW)
# # ---------------------------
# @app.route("/profile")
# def profile_page():
#     if 'user_id' not in session:
#         flash("⚠️ Please log in to view your profile.", "warning")
#         return redirect(url_for('login_page'))
    
#     user_id = session['user_id']
#     results = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.date_taken.desc()).all()
    
#     return render_template("profile.html", results=results)

# # ---------------------------
# # 🔹 RUN APP
# # ---------------------------
# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'qwertyuiopasdfghjkl'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/leetflix'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Models ---
class Users(db.Model):
    __tablename__ = 'users'
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    results = db.relationship('QuizResult', backref='user', lazy=True)

class Login(db.Model):
    __tablename__ = 'login'
    sno = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    dateTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    show_name = db.Column(db.String(255), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    options = db.relationship('Option', backref='question', lazy=True)

class Option(db.Model):
    __tablename__ = 'options'
    option_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.sno'), nullable=False)
    show_name = db.Column(db.String(100), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)

# --- Main Routes ---
@app.route("/")
def home():
    return render_template('trivia.html')

@app.route("/seasons/<show_name>")
def seasons_page(show_name):
    return render_template('seasons.html', show_name=show_name)

@app.route("/leaderboard")
def leaderboard():
    scores = db.session.query(QuizResult, Users.name).join(Users, QuizResult.user_id == Users.sno).order_by(QuizResult.score.desc()).all()
    return render_template('leaderboard.html', scores=scores)

@app.route("/profile")
def profile_page():
    if 'user_id' not in session:
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for('login_page'))
    user_id = session['user_id']
    results = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.date_taken.desc()).all()
    return render_template("profile.html", results=results)

# --- Authentication Routes ---
@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_name'] = user.email.split('@')[0]
            session['user_id'] = user.sno
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password!", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists.", "warning")
            return redirect(url_for('login_page'))
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = Users(name=name, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login_page'))
    return render_template('register.html')

# --- Quiz Routes ---
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "GET":
        # This block starts a new quiz
        show_name = request.args.get('show_name')
        season = request.args.get('season', type=int)
        
        if show_name and season:
            questions = Question.query.filter_by(show_name=show_name, season=season).all()
            if not questions:
                flash(f"No questions found for {show_name} Season {season}.", "warning")
                return redirect(url_for("home"))
            
            # Set up a new quiz in the session, preserving login info
            session['question_ids'] = [q.question_id for q in questions]
            session['q_index'] = 0
            session['score'] = 0
            session['show_name'] = show_name
            session['season'] = season
            session['total_questions'] = len(questions)
        else:
            # If arriving at /quiz without parameters, redirect home
            return redirect(url_for("home"))

    # Check if a quiz is in progress before proceeding
    if 'q_index' not in session or 'question_ids' not in session:
        flash("Please select a quiz to start.", "warning")
        return redirect(url_for("home"))

    if request.method == "POST":
        # This block handles a submitted answer
        selected_option_id = request.form.get("option")
        if selected_option_id:
            option = Option.query.get(int(selected_option_id))
            if option and option.is_correct:
                session['score'] += 1
        # Move to the next question index
        session['q_index'] += 1

    q_index = session.get('q_index', 0)
    total_questions = session.get('total_questions', 0)

    # Check if the quiz is over
    if q_index >= total_questions:
        return redirect(url_for("quiz_result", score=session.get('score', 0), total=total_questions))

    # Fetch and display the current question
    current_question_id = session['question_ids'][q_index]
    question = Question.query.get(current_question_id)
    
    return render_template("quiz.html", question=question)


@app.route("/quiz_result")
def quiz_result():
    score = request.args.get("score", 0, type=int)
    total = request.args.get("total", 0, type=int)
    
    # Save score to DB if a user is logged in
    if 'user_id' in session:
        new_result = QuizResult(
            user_id=session['user_id'],
            show_name=session.get('show_name'),
            season=session.get('season'),
            score=score,
            total_questions=total
        )
        db.session.add(new_result)
        db.session.commit()
    
    # Clean up quiz-specific session variables
    session.pop('question_ids', None)
    session.pop('q_index', None)
    session.pop('score', None)
    session.pop('show_name', None)
    session.pop('season', None)
    session.pop('total_questions', None)
    
    return render_template("result.html", score=score, total=total)

if __name__ == '__main__':
    app.run(debug=True)


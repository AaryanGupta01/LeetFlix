from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_very_secret_key'
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
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    show_name = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.sno'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.sno'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizResult(db.Model):
    # ... (rest of your models are unchanged)
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.sno'), nullable=False)
    show_name = db.Column(db.String(100), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)

class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    qno = db.Column(db.Integer, nullable=True)
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

class Login(db.Model):
    __tablename__ = 'login'
    sno = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    dateTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# --- Main Routes ---
@app.route("/")
def home():
    # We will pass the logged-in user ID to the template
    user_id = session.get('user_id')
    return render_template('trivia.html', user_id=user_id)

# --- NEW DISCUSSION ROUTES ---
@app.route("/discussion/<show_name>")
def discussion_page(show_name):
    # Fetch posts and comments for the show
    posts = Post.query.filter_by(show_name=show_name).order_by(Post.created_at.desc()).all()
    user_id = session.get('user_id')
    return render_template('discussion.html', posts=posts, show_name=show_name, user_id=user_id)

@app.route("/add_post/<show_name>", methods=['POST'])
def add_post(show_name):
    if 'user_id' not in session:
        flash("You must be logged in to post.", "warning")
        return redirect(url_for('login_page'))

    title = request.form.get('title')
    content = request.form.get('content')
    author_id = session['user_id']

    if title and content:
        new_post = Post(title=title, content=content, show_name=show_name, author_id=author_id)
        db.session.add(new_post)
        db.session.commit()
        flash("Post created successfully!", "success")
    else:
        flash("Title and content are required.", "danger")
        
    return redirect(url_for('discussion_page', show_name=show_name))

@app.route("/add_comment/<int:post_id>", methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        flash("You must be logged in to comment.", "warning")
        return redirect(url_for('login_page'))

    content = request.form.get('comment_content')
    user_id = session['user_id']
    
    post = Post.query.get_or_404(post_id)

    if content:
        new_comment = Comment(content=content, post_id=post.id, user_id=user_id)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added!", "success")
    else:
        flash("Comment cannot be empty.", "danger")

    return redirect(url_for('discussion_page', show_name=post.show_name))


# --- Authentication Routes (UPDATED) ---
@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # --- IMPORTANT: Store user's unique ID in the session ---
            session['user_id'] = user.sno 
            session['user_name'] = user.email.split('@')[0]
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password!", "danger")
    return render_template('login.html')

# (The rest of your routes: logout, register, quiz, seasons, etc. remain the same)
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

@app.route("/seasons/<show_name>")
def seasons_page(show_name):
    return render_template('seasons.html', show_name=show_name)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "GET":
        show_name = request.args.get('show_name')
        season = request.args.get('season', type=int)
        
        if show_name and season:
            questions = Question.query.filter_by(show_name=show_name, season=season).all()
            if not questions:
                flash(f"No questions found for {show_name} Season {season}.", "warning")
                return redirect(url_for("home"))
            
            session['question_ids'] = [q.question_id for q in questions]
            session['q_index'] = 0
            session['score'] = 0
            session['show_name'] = show_name
            session['season'] = season
            session['total_questions'] = len(questions)
        else:
            # If quiz is started without params, redirect home
            return redirect(url_for("home"))

    if 'q_index' not in session or 'question_ids' not in session:
        flash("Please select a quiz to start.", "warning")
        return redirect(url_for("home"))

    if request.method == "POST":
        selected_option_id = request.form.get("option")
        if selected_option_id:
            option = Option.query.get(int(selected_option_id))
            if option and option.is_correct:
                session['score'] += 1
        session['q_index'] += 1

    q_index = session.get('q_index', 0)
    total_questions = session.get('total_questions', 0)

    if q_index >= total_questions:
        return redirect(url_for("quiz_result"))

    current_question_id = session['question_ids'][q_index]
    question = Question.query.get(current_question_id)
    
    return render_template("quiz.html", question=question, current_q_num=q_index + 1, total_questions=total_questions)


@app.route("/quiz_result")
def quiz_result():
    score = session.get('score', 0)
    total = session.get('total_questions', 0)
    
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
    
    # Clear session data related to the quiz
    session.pop('question_ids', None)
    session.pop('q_index', None)
    session.pop('score', None)
    session.pop('show_name', None)
    session.pop('season', None)
    session.pop('total_questions', None)
    
    return render_template("result.html", score=score, total=total)

@app.route("/profile")
def profile_page():
    if 'user_id' not in session:
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for('login_page'))
    user_id = session['user_id']
    results = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.date_taken.desc()).all()
    return render_template("profile.html", results=results)

@app.route("/leaderboard")
def leaderboard():
    scores = db.session.query(QuizResult, Users.name).join(Users, QuizResult.user_id == Users.sno).order_by(QuizResult.score.desc()).all()
    return render_template('leaderboard.html', scores=scores)


if __name__ == '__main__':
    app.run(debug=True)


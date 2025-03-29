from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):  #ixed class name
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)  #Email must be unique
    password = db.Column(db.String(255), nullable=False)  #Securely hashed
    user_type = db.Column(db.String(20), nullable=False, default="end_user")  # Default user type

    def is_admin(self):
        return self.user_type and self.user_type.lower() == 'admin'  #Prevents NoneType errors

    def set_password(self, password):
        self.password = generate_password_hash(password)  #  Hash password before storing

    def check_password(self, password):
        return check_password_hash(self.password, password)  #  Secure password check
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "user_type": self.user_type
        }


class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationship: A subject can have multiple chapters
    chapters = db.relationship('Chapter', backref='subject', cascade='all, delete-orphan', lazy=True)

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.String(20), unique=True, nullable=False)  # Custom Chapter ID (e.g., "C001")
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    quizzes = db.relationship('Quiz', backref='chapter', cascade='all, delete-orphan', lazy=True)

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  #  Added missing name
    available_quizzes=db.Column(db.String(100),nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=True)
    date_of_quiz = db.Column(db.DateTime, nullable=True)  #  Allow quizzes to have no date initially
    time_duration = db.Column(db.String(10), nullable=True) 
    # e.g., "01:30" (hh:mm)

    # Relationship: A quiz has multiple questions
    questions = db.relationship('Question', backref='quiz', cascade='all, delete-orphan', lazy=True)

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_statement = db.Column(db.String(255), nullable=False)
    quiz_name=db.Column(db.String(255),nullable=True)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.String(100), nullable=False)
    user_answer = db.Column(db.String(100), nullable=True)  # Add user's answer field

class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
 
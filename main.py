from flask import Flask, render_template, request, redirect, url_for, flash,session
from model import db, User, Quiz, Chapter, Subject, Question
from model import *


import os
from werkzeug.security import generate_password_hash, check_password_hash

current_dir = os.path.abspath(os.path.dirname(__file__))
print(current_dir)

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here' 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(current_dir, 'projectdatabase.sqlite3')
db.init_app(app)


#app.config['SESSION_TYPE'] = 'filesystem'
#from flask_session import Session
#Session(app)
#  Securely create an admin user if not present
def create_admin():
    with app.app_context():  #  Ensure DB context
        admin_user = User.query.filter_by(user_type="admin").first()  # FIXED
        
        if admin_user:
            print(" Admin already exists in the database.")
        else:
            print(" Creating admin user...")
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password=generate_password_hash("1234"),  #  Securely hashed password
                user_type="admin"
            )
            db.session.add(admin_user)
            db.session.commit()
            print(" Admin user created successfully!")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']
        check_user = User.query.filter_by(email=user_email).first()
        #user = User.query.filter_by(username=session.get('username')).first()
        if check_user and check_password_hash(check_user.password, user_password):
              # Secure password check
            #session['username'] = User.username
            #session['username'] = User.username 
            
            #session['user_id'] = User.id  #  Store only the ID
            session['username'] = check_user.username
            session['is_admin'] = check_user.is_admin()
            
            if check_user.is_admin():
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid email or password", "error")

    return render_template("login.html")

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == "POST":
        id=request.form.get("id")
        name = request.form.get("name")
        available_quizzes = request.form.get("available_quizzes")  # Get from form input
        chapter_id= request.form.get("chapter_id")
        print(name)   

        new_quiz = Quiz(id=id, name=name, available_quizzes=available_quizzes,chapter_id=chapter_id)
        db.session.add(new_quiz)

        db.session.commit()
        return redirect(url_for('admin_dashboard',id=id,name=name, available_quizzes=available_quizzes))

    # Fetch all subjects and prepare data
    subjects = Subject.query.all()
    quizzes = Quiz.query.all()

    return render_template('admin_dashboard.html', subjects=subjects, quizzes=quizzes)




@app.route('/user_dashboard',methods=['GET'])
def user_dashboard():
    username = User.query.filter_by(username=session.get('username')).first()
    quizzes = Quiz.query.all()
    subjects = Subject.query.all()
    
    # Create dictionaries to store questions and scores for each quiz
    quiz_questions = {}
    quiz_scores = {}
    
    for quiz in quizzes:
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        quiz_questions[quiz.id] = questions
        
        # Calculate score for this quiz
        total_questions = len(questions)
        if total_questions > 0:
            correct_answers = sum(1 for q in questions if q.user_answer == q.correct_option)
            score_percentage = (correct_answers / total_questions) * 100
            quiz_scores[quiz.id] = {
                'correct': correct_answers,
                'total': total_questions,
                'percentage': round(score_percentage, 2)
            }
        else:
            quiz_scores[quiz.id] = {
                'correct': 0,
                'total': 0,
                'percentage': 0
            }
    
    return render_template('user_dashboard.html', 
                         username=username,
                         quizzes=quizzes,
                         subjects=subjects,
                         quiz_questions=quiz_questions,
                         quiz_scores=quiz_scores)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_name = request.form['username']
        user_email = request.form['email']
        user_password = request.form['userpassword']
        user_type = request.form.get('user_type', 'end_user')  #  Ensure a default user type

        if User.query.filter_by(email=user_email).first():
            return "User already exists"

        new_user = User(
            username=user_name,
            email=user_email,
            password=generate_password_hash(user_password),  # Securely hashed password
            user_type=user_type
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('home.html')








@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        subject_name = request.form.get('name')
        if subject_name:
            new_subject = Subject(name=subject_name)
            db.session.add(new_subject)
            db.session.commit()
            flash("Subject added successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('add_subject.html')


@app.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
        flash("Subject deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/add_chapter/<int:subject_id>', methods=['GET', 'POST'])
def add_chapter(subject_id):
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        chapter_name = request.form.get('chapter_name')

        if not chapter_id or not chapter_name:
            flash("Chapter ID and Name are required!", "danger")
        else:
            new_chapter = Chapter(chapter_id=chapter_id, name=chapter_name, subject_id=subject_id)
            db.session.add(new_chapter)
            db.session.commit()
            flash("Chapter added successfully!", "success")
            return redirect(url_for('view_subject', subject_id=subject_id))

    return render_template('add_chapter.html', subject_id=subject_id)



@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        chapter.chapter_id = request.form.get('chapter_id')
        chapter.name = request.form.get('chapter_name')
        db.session.commit()
        flash("Chapter updated successfully!", "success")
        return redirect(url_for('view_subject', subject_id=chapter.subject_id))

    return render_template('edit_chapter.html', chapter=chapter)



@app.route('/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!", "success")
    return redirect(url_for('view_subject', subject_id=subject_id))



@app.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz(chapter_id):
    if request.method == 'POST':
        quiz_name = request.form.get('name')
        if quiz_name:
            new_quiz = Quiz(name=quiz_name, chapter_id=chapter_id)
            db.session.add(new_quiz)
            db.session.commit()
            flash("Quiz added successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('add_quiz.html', chapter_id=chapter_id)


@app.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if quiz:
        db.session.delete(quiz)
        db.session.commit()
        flash("Quiz deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):
    if request.method == 'POST':
        question_statement = request.form.get('question_statement')
        correct_option = request.form.get('correct_option')
        
        if question_statement and correct_option:
            # Get the quiz to access its name
            quiz = Quiz.query.get(quiz_id)
            if quiz:
                new_question = Question(
                    quiz_id=quiz_id,
                    question_statement=question_statement,
                    quiz_name=quiz.name,  # Use the quiz's name field
                    correct_option=correct_option,
                    option1=request.form.get('option1'),
                    option2=request.form.get('option2'),
                    option3=request.form.get('option3'),
                    option4=request.form.get('option4')
                )
                db.session.add(new_question)
                db.session.commit()
                flash("Question added successfully!", "success")
                
                # Redirect back to the same page to add more questions
                return redirect(url_for('add_question', quiz_id=quiz_id))
            else:
                flash("Quiz not found!", "error")
                return redirect(url_for('admin_dashboard'))

    return render_template('add_question.html', quiz_id=quiz_id)








@app.route('/subject/<int:subject_id>')
def view_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('subject_details.html', subject=subject, chapters=chapters)




@app.route('/sql')
def sql():
    data_user = User.query.all()
    return render_template('home.html', all_user=data_user)

@app.route('/submit_answer/<int:question_id>', methods=['POST'])
def submit_answer(question_id):
    question = Question.query.get_or_404(question_id)
    user_answer = request.form.get('answer')
    
    if user_answer:
        question.user_answer = user_answer
        db.session.commit()
        
        # Show appropriate flash message
        if user_answer == question.correct_option:
            flash("Correct answer!", "success")
        else:
            flash("Incorrect answer. Try again!", "danger")
    
    return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()  #  Ensure the admin exists

    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

class Cards(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	course = db.Column(db.String(50), nullable=False)
	question = db.Column(db.Text, nullable=False)
	answer = db.Column(db.Text, nullable=False)
	date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
	interval = db.Column(db.Integer, nullable=False, default=1)
	date_rev = db.Column(db.DateTime, nullable=False, default=datetime.now)
	last_rev = db.Column(db.DateTime, nullable=False, default=datetime.now)
	def __repr__(self):
		return "question: " + str(self.question)

class Total(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	total = db.Column(db.Integer, default=1)
	result = db.Column(db.Integer, default=0)
	date = db.Column(db.DateTime, nullable=False, default=datetime.today())
	course = db.Column(db.String(50), nullable=False, default="all")
	def __repr__(self):
		return str(self.total)

@app.route("/")
def index():
	courselist = Cards.query.with_entities(Cards.course)
	hour = datetime.now().replace(hour=19, minute=0, second=0)
	now = datetime.now()
	return render_template("index.html", courselist=courselist, hour=hour, now=now)

@app.route("/carte", methods=['GET', 'POST'])
def cards():
    all_cards = Cards.query.order_by(Cards.date_rev.asc()).all()
    courselist = Cards.query.with_entities(Cards.course)
    today = datetime.now().date()
    hour = datetime.now().replace(hour=19, minute=0, second=0)
    now = datetime.now()
    return render_template("posts.html", cards=all_cards, courselist=courselist, today=today, hour=hour, now=now)

@app.route("/cours/<course>", methods=["GET", "POST"])
def course(course):
	if request.method == "POST":
		card_question = request.form["question"]
		card_question = card_question[0].upper() + card_question[1:]
		card_answer = request.form["answer"]
		card_answer = card_answer[0].upper() + card_answer[1:]
		card_course = request.form["course"]
		card_course = card_course[0].upper() + card_course[1:]
		new_card = Cards(question=card_question, answer=card_answer, course=card_course)
		db.session.add(new_card)
		db.session.commit()
		return redirect(str("/cours/")+course)
	else:
		today = datetime.now().date()
		all_cards = Cards.query.filter(Cards.course == course).order_by(Cards.date_rev.asc()).all()
		if len(all_cards):
		    courselist = Cards.query.with_entities(Cards.course)
		    hour = datetime.now().replace(hour=19, minute=0, second=0)
		    now = datetime.now()
		    return render_template("course.html", cards=all_cards, courselist=courselist, currentc=course, today=today, hour=hour, now=now)
		else:
		    return redirect("/carte")

@app.route("/carte/delete/<int:id>")
def delete_card(id):
    card = Cards.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    return redirect("/carte")

@app.route("/<course>/delete/<int:id>")
def delete_card_course(id, course):
    card = Cards.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    return redirect(str("/cours/")+course)

@app.route("/carte/edit/<int:id>", methods=['GET', 'POST'])
def edit_card(id):
    card = Cards.query.get_or_404(id)
    if request.method == "POST":
        card.question = request.form['question']
        card.question = card.question[0].upper() + card.question[1:]
        card.answer = request.form['answer']
        card.answer = card.answer[0].upper() + card.answer[1:]
        card.course = request.form['course']
        card.course = card.course[0].upper() + card.course[1:]
        if 'reset' in request.form:
        	card.interval = 1
        	card.date_rev = datetime.now().date()
        db.session.commit()
        return redirect("/carte")
    else:
    	today = datetime.now().date()
    	hour = datetime.now().replace(hour=19, minute=0, second=0)
    	now = datetime.now()
    	return render_template("posts_edit.html", card=card, today=today, hour=hour, now=now)

@app.route("/<course>/edit/<int:id>", methods=['GET', 'POST'])
def edit_card_course(id, course):
    card = Cards.query.get_or_404(id)
    if request.method == "POST":
        card.question = request.form['question']
        card.question = card.question[0].upper() + card.question[1:]
        card.answer = request.form['answer']
        card.answer = card.answer[0].upper() + card.answer[1:]
        card.course = request.form['course']
        card.course = card.course[0].upper() + card.course[1:]
        if 'reset' in request.form:
        	card.interval = 1
        	card.date_rev = datetime.now().date()
        db.session.commit()
        return redirect(str("/cours/")+course)
    else:
    	today = datetime.now().date()
    	hour = datetime.now().replace(hour=19, minute=0, second=0)
    	now = datetime.now()
    	return render_template("posts_edit.html", card=card, current=course, today=today, hour=hour, now=now)

@app.route("/quiz")
def quiz_card():
	today = datetime.now().date()
	tomorrow = datetime.now().date() + timedelta(days=1)
	courselist = Cards.query.with_entities(Cards.course)
	all_cards = Cards.query.filter(tomorrow > Cards.date_rev).order_by(Cards.date_rev.asc()).all()
	hour = datetime.now().replace(hour=19, minute=0, second=0)
	now = datetime.now()
	return render_template("quiz.html",cards=all_cards, courselist=courselist, today=today, hour=hour, now=now)

@app.route("/quiz/infinity")
def infinity():
	courselist = Cards.query.with_entities(Cards.course)
	all_cards = Cards.query.order_by(Cards.date_rev.asc()).all()
	total = len(all_cards)
	hour = datetime.now().replace(hour=19, minute=0, second=0)
	now = datetime.now()
	return render_template("infinty.html",cards=all_cards, courselist=courselist, hour=hour, now=now, total=total)

@app.route("/quiz/<course>", methods=["GET", "POST"])
def quizcourse(course):
	today = datetime.now().date()
	tomorrow = datetime.now().date() + timedelta(days=1)
	all_cards = Cards.query.filter(tomorrow > Cards.date_rev).filter(Cards.course == course).order_by(Cards.date_rev.asc()).all()
	courselist = Cards.query.with_entities(Cards.course)
	hour = datetime.now().replace(hour=19, minute=0, second=0)
	now = datetime.now()
	return render_template("quizcourse.html", cards=all_cards, courselist=courselist, current=course, today=today, now=now, hour=hour)

@app.route("/quiz/<course>/sucess/<int:id>")
def quiz_course_success(id, course):
    card = Cards.query.get_or_404(id)
    card.interval = card.interval*2
    card.date_rev = card.date_rev+timedelta(days=card.interval)
    card.last_rev = datetime.now().date()
    db.session.commit()
    return redirect(str("/quiz/")+course)

@app.route("/quiz/<course>/fail/<int:id>")
def quiz_course_fail(id, course):
    card = Cards.query.get_or_404(id)
    card.interval = 1
    card.date_rev = datetime.now().date()+timedelta(days=1)
    card.last_rev = datetime.now().date()
    db.session.commit()
    return redirect(str("/quiz/")+course)

@app.route("/carte/quiz/sucess/<int:id>")
def quiz_success(id):
    card = Cards.query.get_or_404(id)
    card.interval = card.interval*2
    card.date_rev = card.date_rev+timedelta(days=card.interval)
    card.last_rev = datetime.now().date()
    db.session.commit()
    return redirect("/quiz")

@app.route("/carte/quiz/fail/<int:id>")
def quiz_fail(id):
    card = Cards.query.get_or_404(id)
    card.interval = 1
    card.date_rev = datetime.now().date()+timedelta(days=1)
    card.last_rev = datetime.now().date()
    db.session.commit()
    return redirect("/quiz")

@app.route("/carte/new", methods=["GET", "POST"])
def new_card():
    if request.method == "POST":
        card_question = request.form["question"]
        card_question = card_question[0].upper() + card_question[1:]
        card_answer = request.form["answer"]
        card_answer = card_answer[0].upper() + card_answer[1:]
        card_course = request.form["course"]
        card_course = card_course[0].upper() + card_course[1:]
        new_card = Cards(question=card_question, answer=card_answer, course=card_course)
        db.session.add(new_card)
        db.session.commit()
        return redirect("/carte")
    else:
    	courselist = Cards.query.with_entities(Cards.course)
    	hour = datetime.now().replace(hour=19, minute=0, second=0)
    	now = datetime.now()
    	return render_template("posts_new.html", courselist=courselist, hour=hour, now=now)

@app.route("/carte/new/<course>", methods=["GET", "POST"])
def new_card_course(course):
    if request.method == "POST":
        card_question = request.form["question"]
        cardquestion = card_question[0].upper() + card_question[1:]
        card_answer = request.form["answer"]
        cardanswer = card_answer[0].upper() + card_answer[1:]
        card_course = request.form["course"]
        cardcourse = card_course[0].upper() + card_course[1:]
        new_card = Cards(question=cardquestion, answer=cardanswer, course=card_course)
        db.session.add(new_card)
        db.session.commit()
        return redirect(str("/cours/")+course)
    else:
    	courselist = Cards.query.with_entities(Cards.course)
    	hour = datetime.now().replace(hour=19, minute=0, second=0)
    	now = datetime.now()
    	return render_template("posts_new.html", courselist=courselist, current=course, hour=hour, now=now)


if __name__ == "__main__":
    app.run()

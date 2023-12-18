from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func

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
		card_question = request.form["question"].capitalize()
		card_answer = request.form["answer"].capitalize()
		card_course = request.form["course"].capitalize()
		new_card = Cards(question=card_question, answer=card_answer, course=card_course)
		db.session.add(new_card)
		db.session.commit()
		return redirect(str("/cours/")+course)
	else:
		today = datetime.now().date()
		all_cards = Cards.query.filter(Cards.course == course).order_by(Cards.date_rev.asc()).all()
		courselist = Cards.query.with_entities(Cards.course)
		hour = datetime.now().replace(hour=19, minute=0, second=0)
		now = datetime.now()
		return render_template("course.html", cards=all_cards, courselist=courselist, currentc=course, today=today, hour=hour, now=now)

@app.route("/carte/delete/<int:id>")
def delete_card(id):
    card = Cards.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    return redirect("/carte")

@app.route("/carte/edit/<int:id>", methods=['GET', 'POST'])
def edit_card(id):
    card = Cards.query.get_or_404(id)
    if request.method == "POST":
        card.question = request.form['question'].capitalize()
        card.answer = request.form['answer'].capitalize()
        card.course = request.form['course'].capitalize()
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
        card.question = request.form['question'].capitalize()
        card.answer = request.form['answer'].capitalize()
        card.course = request.form['course'].capitalize()
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
	yesterday = datetime.now().date() - timedelta(days=1)
	tomorrow = datetime.now().date() + timedelta(days=1)
	courselist = Cards.query.with_entities(Cards.course)
	all_cards = Cards.query.filter(tomorrow > Cards.date_rev).order_by(Cards.date_rev.asc()).all()
	hour = datetime.now().replace(hour=19, minute=0, second=0)
	now = datetime.now()
	total = len(all_cards)
	totalquiz = Total.query.filter(Total.course == "all").order_by(Total.date.desc()).first()
	if totalquiz.date.date() != today:
		if yesterday < totalquiz.date.date() < tomorrow:
			return render_template("quiz.html",cards=all_cards, courselist=courselist, today=today, hour=hour, now=now, total=total, totalquiz=totalquiz)
	else:
		if total > 0:
			new_test = Total(total=total)
			db.session.add(new_test)
			db.session.commit()
			totalquiz = Total.query.filter(yesterday < Total.date, Total.date < tomorrow, Total.course == "all")
	return render_template("quiz.html",cards=all_cards, courselist=courselist, today=today, hour=hour, now=now, total=total, totalquiz=totalquiz)

@app.route("/quiz/<course>", methods=["GET", "POST"])
def quizcourse(course):
	today = datetime.now().date()
	yesterday = datetime.now().date() - timedelta(days=1)
	tomorrow = datetime.now().date() + timedelta(days=1)
	all_cards = Cards.query.filter(tomorrow > Cards.date_rev).filter(Cards.course == course).order_by(Cards.date_rev.asc()).all()
	courselist = Cards.query.with_entities(Cards.course)
	hour = datetime.now().replace(hour=19, minute=0, second=0)
	now = datetime.now()
	total = len(all_cards)
	if Total.query.filter(yesterday < Total.date, Total.date < tomorrow).filter(Total.course == course).first() != None:
		totalquiz = Total.query.filter(yesterday < Total.date, Total.date < tomorrow).filter(Total.course == course)
		if yesterday < totalquiz.date.date() < tomorrow:
			return render_template("quizcourse.html",cards=all_cards, courselist=courselist,current=course, today=today, hour=hour, now=now, total=total, totalquiz=totalquiz)
	else:
		if total > 0:
			new_test = Total(total=total, course=course)
			db.session.add(new_test)
			db.session.commit()
			totalquiz = Total.query.filter(yesterday < Total.date, Total.date < tomorrow, Total.course == course)
			return render_template("quizcourse.html", cards=all_cards, courselist=courselist, current=course, today=today, now=now, hour=hour, totalquiz=totalquiz)
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
    yesterday = datetime.now().date() - timedelta(days=1)
    tomorrow = datetime.now().date() + timedelta(days=1)
    resultq = Total.query.filter(yesterday < Total.date, Total.date < tomorrow, Total.course == "all").first()
    resultq.result=resultq.result+1
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
        card_question = request.form["question"].capitalize()
        card_answer = request.form["answer"].capitalize()
        card_course = request.form["course"].capitalize()
        new_card = Cards(question=card_question, answer=card_answer, course=card_course)
        yesterday = datetime.now().date() - timedelta(days=1)
        tomorrow = datetime.now().date() + timedelta(days=1)
        totalquiz = Total.query.filter(yesterday < Total.date, Total.date < tomorrow, Total.course == "all").first()
        totalquiz.total = totalquiz.total+1
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
        card_question = request.form["question"].capitalize()
        card_answer = request.form["answer"].capitalize()
        card_course = request.form["course"].capitalize()
        new_card = Cards(question=card_question, answer=card_answer, course=card_course)
        yesterday = datetime.now().date() - timedelta(days=1)
        tomorrow = datetime.now().date() + timedelta(days=1)
        totalquiz = Total.query.filter(yesterday < Total.date, Total.date < tomorrow, Total.course == "all").first()
        totalquiz.total = totalquiz.total+1
        db.session.add(new_card)
        db.session.commit()
        return redirect(str("/cours/")+course)
    else:
    	courselist = Cards.query.with_entities(Cards.course)
    	hour = datetime.now().replace(hour=19, minute=0, second=0)
    	now = datetime.now()
    	return render_template("posts_new.html", courselist=courselist, current=course, hour=hour, now=now)
    	 

if __name__ == "__main__":
    app.run(debug=True)

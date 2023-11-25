from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
	date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	interval = db.Column(db.Integer, nullable=False, default=2)
	def __repr__(self):
		return "question: " + str(self.question)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/carte", methods=['GET', 'POST'])
def cards():
    all_cards = Cards.query.order_by(Cards.date_created.desc()).all()
    courselist = Cards.query.with_entities(Cards.course)
    return render_template("posts.html", cards=all_cards, courselist=courselist)

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
        db.session.commit()
        return redirect("/carte")
    else:
        return render_template("posts_edit.html", card=card)

@app.route("/carte/new", methods=["GET", "POST"])
def new_card():
    if request.method == "POST":
        card_question = request.form["question"].capitalize()
        card_answer = request.form["answer"].capitalize()
        card_course = request.form["course"].capitalize()
        new_card = Cards(question=card_question, answer=card_answer, course=card_course)
        db.session.add(new_card)
        db.session.commit()
        return redirect("/carte")
    else:
    	courselist = Cards.query.with_entities(Cards.course)
    	return render_template("posts_new.html", courselist=courselist)

if __name__ == "__main__":
    app.run(debug=True)
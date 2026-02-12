from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

def days_late(due_date_str):
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    today = date.today()
    diff = (today - due_date).days
    return diff if diff > 0 else 0


# DATABASE MODEL
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.String(20), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # NEW → 0 = incomplete , 1 = completed
    complete = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Task %r>' % self.id


# HOME PAGE
@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        task_content = request.form["content"]
        task_due_date = request.form["due_date"]

        new_task = Todo(content=task_content, due_date=task_due_date)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except:
            return "Error adding task"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        today = datetime.today().date()
        delays = {}
        for task in tasks:
            delays[task.id] = days_late(task.due_date)

        return render_template('index.html', tasks=tasks, today=today, delays=delays)

    tasks = Todo.query.order_by(Todo.date_created).all()
    return render_template("index.html", tasks=tasks)


# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    task = Todo.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect("/")
    except:
        return "Error deleting task"


# TOGGLE COMPLETE / INCOMPLETE
@app.route('/complete/<int:id>')
def complete(id):
    task = Todo.query.get_or_404(id)

    # Toggle value (0 -> 1 , 1 -> 0)
    task.complete = 0 if task.complete == 1 else 1

    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Error updating task status"


# UPDATE

@app.route("/update/<int:id>", methods=["GET","POST"])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == "POST":
        task.content = request.form["content"]
        task.due_date = request.form["due_date"]

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Error updating task"

    return render_template("update.html", task=task)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
app.secret_key = "super-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    tags = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
   
    @property
    def date_created(self):
        return self.created_at
with app.app_context():
    db.create_all()
# ---------- routes ----------
@app.route("/")
def index():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template("index.html", notes=notes, page="home")

@app.route("/add", methods=["GET", "POST"])
def add_note():
    if request.method == "POST":
        title   = request.form["title"]
        content = request.form["content"]
        if not title or not content:
            flash("Title and Content cannot be empty!", "danger")
            return redirect(url_for("add_note"))

        db.session.add(Note(title=title, content=content))
        db.session.commit()
        flash("Note added successfully!", "success")
        return redirect(url_for("index"))
    return render_template("add_note.html", page="add")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_note(id):
    note = Note.query.get_or_404(id)
    if request.method == "POST":
        note.title   = request.form["title"]
        note.content = request.form["content"]
        db.session.commit()
        flash("Note updated!", "success")
        return redirect(url_for("index"))
    return render_template("edit_note.html", note=note, page="edit")

@app.route("/delete/<int:id>")
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted.", "success")
    return redirect(url_for("index"))

@app.route("/")
def home():
    search_query = request.args.get("search", "")  
    if search_query:
        notes = Note.query.filter(Note.title.contains(search_query) | Note.content.contains(search_query)).order_by(Note.created_at.desc()).all()
    else:
        notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template("all_notes.html", notes=notes, search_query=search_query, page="home")

# ---------- auto‑create DB ----------
if __name__ == "__main__":
    with app.app_context():
        if not Path("notes.db").exists():
            db.create_all()
    app.run(debug=True)

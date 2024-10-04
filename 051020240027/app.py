from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)  # Исправлено: заменено name на __name__
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedules.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(80), unique=True, nullable=False)
    events = db.relationship('Event', backref='schedule', lazy=True)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    when = db.Column(db.String(120), nullable=False)
    where = db.Column(db.String(120), nullable=True)
    who = db.Column(db.String(120), nullable=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)


# Оберните вызов db.create_all() в контекст приложения
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_schedule', methods=['POST'])
def create_schedule():
    password = request.form.get('password')
    new_schedule = Schedule(password=password)
    db.session.add(new_schedule)
    db.session.commit()
    return redirect(url_for('schedule', password=password))


@app.route('/schedule/<password>', methods=['GET', 'POST'])
def schedule(password):
    schedule = Schedule.query.filter_by(password=password).first()
    if request.method == 'POST':
        when = request.form.get('when')
        where = request.form.get('where')
        who = request.form.get('who')

        if when:
            new_event = Event(when=when, where=where, who=who, schedule=schedule)
            db.session.add(new_event)
            db.session.commit()

    events = Event.query.filter_by(schedule_id=schedule.id).all()
    return render_template('schedule.html', schedule=schedule, events=events)


@app.route('/view_schedule', methods=['POST'])
def view_schedule():
    password = request.form.get('password')
    schedule = Schedule.query.filter_by(password=password).first()
    if schedule:
        return redirect(url_for('schedule', password=password))
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':  # Исправлено: заменено name на __name__
    app.run(debug=True)
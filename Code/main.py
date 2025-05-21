from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import random
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    thumbnail = db.Column(db.String(200))
    large_picture = db.Column(db.String(200)) # Store the large picture URL

    def __repr__(self):
        return f'<User {self.first_name} {self.last_name}>'


def load_users_from_api(num_users):
    url = f'https://randomuser.me/api/?results={num_users}'
    response = requests.get(url)
    data = response.json()
    for result in data['results']:
        user = User(
            gender=result['gender'],
            first_name=result['name']['first'],
            last_name=result['name']['last'],
            phone=result['phone'],
            email=result['email'],
            country=result['location']['country'],
            city=result['location']['city'],
            thumbnail=result['picture']['thumbnail'],
            large_picture=result['picture']['large']
        )
        db.session.add(user)
    db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            num_users = int(request.form['num_users'])
            load_users_from_api(num_users)
            return redirect(url_for('index'))
        except ValueError:
            return render_template('index.html', users=User.query.all(), error="Invalid number of users.")

    users = User.query.all()
    return render_template('index.html', users=users, error=None)


@app.route('/user/<int:user_id>')
def user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user.html', user=user)


@app.route('/random')
def random_user():
    all_users = User.query.all()
    if all_users:
        random_user = random.choice(all_users)
        return render_template('user.html', user=random_user)
    else:
        return "No users in the database."


@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404


def create_db():
    db.create_all()
    if User.query.count() == 0:
        load_users_from_api(1000)


with app.app_context():
    create_db()


if __name__ == '__main__':
    app.run()

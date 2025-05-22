"""
Flask-приложение для отображения информации о пользователях, полученной из API randomuser.me.

Основные функции:
- Отображение списка пользователей.
- Отображение детальной информации о пользователе.
- Загрузка пользователей из API.

Используемые библиотеки:
- flask
- flask_sqlalchemy
- requests
- random
- os
"""


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
    """
    Представляет пользователя в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя (первичный ключ).
        gender (str): Пол пользователя.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        phone (str): Номер телефона.
        email (str): Email-адрес.
        country (str): Страна.
        city (str): Город.
        thumbnail (str): URL маленького изображения.
        large_picture (str): URL большого изображения.
    """

    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    thumbnail = db.Column(db.String(200))
    large_picture = db.Column(db.String(200))

    def __repr__(self):
        """
        Возвращает строковое представление объекта User.
        """

        return f'<User {self.first_name} {self.last_name}>'


def load_users_from_api(num_users):
    """
    Загружает пользователей из API и сохраняет их в базе данных.

    Args:
        num_users (int): Количество пользователей для загрузки.
    """

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
    """
    Обрабатывает запросы к главной странице ("/").

    При GET-запросе:
        Отображает список пользователей и форму загрузки.
    При POST-запросе:
        Загружает указанное количество пользователей из API и перенаправляет на главную страницу.

    Returns:
        str: HTML-код главной страницы.
    """

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
    """
    Обрабатывает запросы к странице с информацией о пользователе ("/user/<user_id>").

    Args:
        user_id (int): ID пользователя.

    Returns:
        str: HTML-код страницы с информацией о пользователе.
    """

    user = User.query.get_or_404(user_id)
    return render_template('user.html', user=user)


@app.route('/random')
def random_user():
    """
    Обрабатывает запрос к странице со случайным пользователем ("/random").

    Returns:
        str: HTML-код страницы с информацией о случайном пользователе.
    """

    all_users = User.query.all()
    if all_users:
        random_user = random.choice(all_users)
        return render_template('user.html', user=random_user)
    else:
        return "No users in the database."


@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404


def create_db():
    """
    Создает таблицу базы данных и загружает начальные данные, если база данных пуста.
    """

    db.create_all()
    if User.query.count() == 0:
        load_users_from_api(1000)


with app.app_context():
    create_db()


if __name__ == '__main__':
    app.run()

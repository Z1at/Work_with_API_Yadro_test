import unittest
from Code.main import app, db, User


class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

            user1 = User(gender='male', first_name='John', last_name='Doe', phone='123-456-7890',
                         email='john.doe@example.com', country='USA', city='New York',
                         thumbnail='http://example.com/thumbnail.jpg', large_picture='http://example.com/large.jpg')
            user2 = User(gender='female', first_name='Jane', last_name='Smith', phone='987-654-3210',
                         email='jane.smith@example.com', country='Canada', city='Toronto',
                         thumbnail='http://example.com/thumbnail2.jpg', large_picture='http://example.com/large2.jpg')
            db.session.add_all([user1, user2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_page(self):
        with app.app_context():
            user = User.query.filter_by(first_name='John').first()
            response = self.app.get(f'/user/{user.id}')
            self.assertEqual(response.status_code, 200)
            html_content = response.data.decode('utf-8')
            self.assertIn('John Doe', html_content)
            self.assertIn('john.doe@example.com', html_content)

    def test_random_user_page(self):
        with app.app_context():
            response = self.app.get('/random')
            self.assertEqual(response.status_code, 200)
            html_content = response.data.decode('utf-8')

            self.assertTrue(any(name in html_content for name in ['John Doe', 'Jane Smith']))

    def test_load_users_from_api(self):
        with app.app_context():
            initial_count = User.query.count()

        response = self.app.post('/', data=dict(num_users=5), follow_redirects=True)

        with app.app_context():
            new_count = User.query.count()
        self.assertGreaterEqual(new_count, initial_count + 1)

    def test_invalid_user_id(self):
        response = self.app.get('/user/9999')
        self.assertEqual(response.status_code, 404)
        html_content = response.data.decode('utf-8')
        self.assertIn('Not Found', html_content)


if __name__ == '__main__':
    unittest.main()

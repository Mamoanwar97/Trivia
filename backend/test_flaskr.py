import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:1234@{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

    def test_paging_questions(self):
        response = self.client().get('/questions?page=1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_error_paging_questions(self):
        response = self.client().get('/questions?page=10000000')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_search_questions(self):
        response = self.client().post('/questions/search', json={'searchTerm': 'Caged Bird Sings'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['total_questions'], 1)


    def test_delete_question(self):
        question = Question(question="dummy", answer="dummy", difficulty=1,category='1')
        question.insert()
        response = self.client().delete('/questions/{}'.format(question.id))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_non_existing_question(self):
        response = self.client().delete('/questions/1211256')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')
    
    def test_add_questions(self):
        response = self.client().post('/questions', json={'question': 'dummy', 'answer': 'dummy', 'difficulty': 1, 'category': 1})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_error_add_questions(self):
        response = self.client().post('/questions', json={'question': 'dummy', 'answer': '', 'category': 1})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request error')

    def test_get_by_category(self):
        response = self.client().get('/categories/2/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 4)
        self.assertEqual(len(data['questions']), 4)
    
    def test_quizzes(self):
        response = self.client().post('/quizzes', 
        json={
            'previous_questions': [17],
            'quiz_category': {
                'type': 'Art',
                'id': 2
            }})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 2)
        self.assertEqual(data['end'], False)
        self.assertNotEqual(data['question']['id'], 17)

    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

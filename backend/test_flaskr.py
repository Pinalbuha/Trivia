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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','host123','localhost:5432', self.database_name)

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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    ##_________________________________________questions__________________________##
    
    def test_get_questions(self):  

        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']), 10)
        self.assertTrue(data['categories'])


    def test_404_sent_requesting_questions_beyond_vaild_page(self): 

        res = self.client().get('/questions?page=1000000')
        data=json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], "Resource not found")
        

    ##_______________________________________/categories___________________________________##
    def test_get_categories(self):
        res = self.client().get('/categories') 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']), 6)


    def test_404_sent_requesting_non_existing_category(self):
        res = self.client().get('/categories/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    ##_______________________________________/Delete Questions ___________________________________##
   
    
    def test_delete_question(self):
        question = Question(question="is a test?",
                            answer='yes',
                            category=1,
                             difficulty=1)
        question.insert()

        q_id = question.id
        questions_before = Question.query.all()

        response = self.client().delete('/questions/{}'.format(q_id))
        data = json.loads(response.data)

        questions_after = Question.query.all()
        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], q_id)
        self.assertTrue(len(questions_before) - len(questions_after) == 1)
        self.assertEqual(question, None)


##_______________________________________create questions___________________________________##

    def test_create_question(self):
        
        add_question ={
            'question' : 'This is just for testing',
            'answer' : 'testing goes successfull',
            'dificulty' : 1,
            'category' : 1
        }
        
        response = self.client().post('/questions', json=add_question)
        data = json.loads(response.data)
       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_create_question(self):
        response = self.client().post('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"Unprocessable entity")

##_______________________________________/search___________________________________##

    def test_search_question(self):
        response = self.client().post('/questions/search', json={
            'searchTerm': 'what'})
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_search_questions(self):
        response = self.client().post('/questions/search', json={'searchTerm': 'xyz'})
        data = json.loads(response.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'], "Resource not found")
##_______________________________________ get questions ___________________________________##

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertTrue(len(data["questions"]))


    def test_422_get_questions_per_category_not_found(self):
        res = self.client().get('/categories/1444/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request error")

##_______________________________________quizzes ___________________________________##

    def test_quiz_play(self):

        request_data = {
            'previous_questions': [5, 9],
            'quiz_category': {
                'type': 'History',
                'id': 4
            }
        }
        res = self.client().post('/quizzes', json=request_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        # Ensures previous questions are not returned
        self.assertNotEqual(data['question']['id'], 5)
        self.assertNotEqual(data['question']['id'], 9)

        # Ensures returned question is in the correct category
        self.assertEqual(data['question']['category'], 4)

    def test_404_play_quiz(self):

        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

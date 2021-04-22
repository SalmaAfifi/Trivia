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
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'postgres', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {'question':'question_test',
        'answer': 'answer_test',
        'difficulty': 1,
        'category': 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_405_sent_req_to_post_category(self):
        res = self.client().post('/categories', json={'id':10})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed :(')


    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
    
    def test_404_get_question_page_doesnot_exist(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found :(')


    def test_delete_question(self):
        res = self.client().delete('/questions/12')
        data = json.loads(res.data)
        delete_question = Question.query.filter(Question.id==23).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(delete_question, None)

    def test_404_delete_question_doesnot_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found :(') 


    def test_post_new_questions(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        new_question= Question.query.filter(Question.question==self.new_question['question']).first()
      
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(new_question)

    def test_422_post_invalid_question(self):
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable :(')  


    def test_post_search_term(self):
        res = self.client().post('/questions_search', json={"searchTerm": 'the'})
        data = json.loads(res.data)
      
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_search_term_invalid(self):
        res = self.client().post('/questions_search', json={"searchTerm": 123})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable :(') 
    

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
      
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)    
        self.assertTrue(data['questions'])    
        self.assertTrue(data['total_questions'])    
        self.assertTrue(data['current_category'])

    def test_404_get_question_category_id_doesnot_exist(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found :(')


    def test_post_quiz(self):
        res = self.client().post('/quizzes', json={"previous_questions":[],
                                "quiz_category":{"type":"Science","id":"1"}})
        data = json.loads(res.data)
      
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)    
        self.assertTrue(data['question']) 

    def test_405_get_quiz(self):
        res = self.client().get('/quizzes', json={"previous_questions":[],
                                "quiz_category":{"type":"Science","id":"1"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed :(' )              
    
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
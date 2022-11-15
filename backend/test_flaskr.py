import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

"""
    TODO
    Write at least one test for each test for successful operation and for expected errors.
"""
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
        self.DB_NAME = os.getenv('DB_NAME', 'trivia') 
        self.database_path = "postgres://{}/{}".format( self.DB_HOST, self.DB_NAME)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "What is the longest River in The World?",
            "answer": "The Nile River",
            "category": 3,
            "difficulty": 3
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

    def test_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_404_categories(self):
        res = self.client().get('/categories/10000')
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data['categories']))
        self.assertTrue(data["total_questions"])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    def test_create_question(self):
        total_before = len(Question.query.all())
        new_question = {
            "question": "What is the longest River in The World?",
            "answer": "The Nile River",
            "category": 3,
            "difficulty": 3
        }
        res = self.client().post("/questions", json=new_question)
        total_after = len(Question.query.all())
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_after, total_before +1)   

    def test_422_if_question_creation_failed(self):
        new_question = {
            'question': 'new_question',
            
            'category': 1,
            "difficulty": 3
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")   

    def test_search_question(self):  
        res = self.client().post("/questions/search", json={"searchTerm":"What is the longest River in The World?"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))      

    def test_search_failur(self):
        res = self.client().post("/questions/search", json={"searchTerm":"jkjk"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    def test_question_by_category(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)
        selection = Question.query.filter(Question.category == 2).all()
        questions = [question.format() for question in selection] 
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"],questions)
        self.assertEqual(data["category"], 2)
        self.assertTrue(data["total_questions"])    

    def test_question_by_categeory_failur(self):    
        res = self.client().get("/categories/9/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")   

    def test_quizzes(self):
        res = self.client().post("/quizzes", json={"previous_questions": [],"quiz_category":{'id':3, 'type':'Geography'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])  


    def test_delete_question(self):
        question = Question(
                question='new_question',
                answer='new_answer',
                category=3,
                difficulty=2)
        question.insert()
        question.insert()
        id = question.id
        res = self.client().delete(f'/questions/{id}')
        data = json.loads(res.data) 

        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_if_deletation_failed(self):
        res = self.client().delete("/questions/1000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")    
  

    def test_quizzes_failur(self):
        res = self.client().post("/quizzes", json={"previous_questions": []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")       
  

# # Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
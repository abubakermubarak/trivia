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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_categories(self):

        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_405_categories(self): 
        res = self.client().patch('/categories')
        data = json.loads(res.data)   
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")


    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["cateogries"])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    def test_create_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post("/questions/50", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")  

    def test_search_question(self):  
        res = self.client().post("/search", json={"searchTerm":"Africa"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"],"What is the largest lake in Africa?") 

    def test_search_failur(self):
        res = self.client().post("/search", json={"searchTerm":"AAA"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    def test_question_by_category(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)
        #questions = Question.query.filter(Question.category == 2).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"])
        self.assertEqual(data["category"], 2)
        self.assertEqual(data["total_questions"])

    def test_question_by_categeory_failur(self):    
        res = self.client().post("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_quizzes(self):
        res = self.client().post("/quizzes", json={"previous_questions": [],"quiz_category":{'id':3, 'type':'Geography'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_quizzes_failur(self):
        res = self.client().post("/quizzes", json={"previous_questions": [],"quiz_category":{'id':14, 'type':'Politics'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")



    def test_delete_question(self):
        res = self.client().delete("/questions/2")  
        data = json.loads(res.data) 

        question = Question.query.filter(Question.id == 2).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(question, None)
        

    def test_422_if_deletation_failed(self):
        res = self.client().delete("/questions/1000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    

    



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def retrieve_categories():
        categories = {}
        try:
            choice = Category.query.order_by(Category.id).all()
            for category in choice:
                categories[category.id] = category.type 

            return jsonify(
                {
                    'success': True,
                    'categories': categories,
                }
            )
        except BaseException:
            abort(405)
  

    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.


    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        
        selection = Question.query.order_by(Question.id).all()
        current_question  = paginate_questions(request, selection)
        categories = Category.query.all()
        if len(current_question) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_question,
            'total_questions' : len(Question.query.all()),
            'categories': {category.id: category.type for category in categories}
        })    

    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                 abort(404)
            question.delete()
            return jsonify(
                {
                    'success': True,
                    "question": question_id
                }
            )
        except BaseException:
            abort(422)

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty)
            question.insert()
            if not(question.question and question.answer and question.category and question.difficulty):
                abort(422)
            return jsonify(
                {
                    "success": True,
                }
            )
        except BaseException:
            abort(422)

    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        current_category = []
        try:
            search = '%{}%'.format(search_term)
            selection = Question.query.order_by(Question.category).filter(Question.question.ilike(search)).all()
            questions = paginate_questions(request, selection)

            categories = Question.query.with_entities(Question.category).order_by(Question.category).filter(Question.question.ilike(search)).all()
            for category in categories:
                for innerlist in category:
                    current_category.append(innerlist)
            if len(selection) == 0:
                abort(404)
            return jsonify({
              'success': True,
              'questions': questions,
              'current_category': current_category,
            'total_questions': len(selection)
            })
        except:
            abort(404)
    
    
    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions", methods=['GET'])
    def question_by_categeory(id):
        if int(id) < 0 or int(id) > 6 :
                abort(404)
        try:
            question = Question.query.order_by(Question.id).filter(Question.category == id).all() 
            formatted_question = paginate_questions(request,question)
            
            return jsonify(
                {
                    "questions": formatted_question,
                    "category": id,
                    "total_questions": len(question),
                    #"current_category": question.category,
                    "success": True
                }
            )
        except BaseException:
            abort(404)

    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.route("/quizzes", methods=['POST'])
    def get_question():
        body = request.get_json()
        if not ('quiz_category' in body and 'previous_questions' in body):
            abort(422)
        previous_question = body.get("previous_questions")
        quiz_category = body.get("quiz_category")
        try:
            
            if quiz_category['type'] == 'click':
                questions = Question.query.filter(Question.id.notin_((previous_question))).all() 
            else:
                questions = Question.query.filter_by(category=quiz_category['id']).filter(Question.id.notin_((previous_question))).all()
            
            selection = questions[random.randrange(
                0, len(questions))].format() if len(questions) > 0 else None

            return jsonify({
                'success':True,
                'question': selection
            })
        except:
            abort(422)    



            

  

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "message": "unprocessable",

        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400,
                       "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return (jsonify({"success": False, "error": 405,
                         "message": "method not allowed"}), ), 405
    @app.errorhandler(500)
    def internal_server_error(error):
        return (jsonify({"success": False, "error": 500,
                         "message": "Internal Server Error"}), ), 500                    
    return app

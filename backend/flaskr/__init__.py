import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(query):
    page = request.args.get('page', 1, type=int)

    # throw error when page is beyond pagination
    if page > len(query):
        abort(404)
    
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in query]

    current_questions = questions[start:end]

    return current_questions

    

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access_Control_Allow_Headers', 'Content-Type, Authorization')
        response.headers.add('Access_Control_Allow_Methods', 'GET, POST, PATCH, PUT, DELETE')
        return response




    # get all categories
    @app.route('/categories', methods=['GET'])
    def all_categories():
        try:
            # Get all categories
            query = Category.query.all()

            # Checking if any categories are avalliable
            if len(query) == 0:
                abort(404)

            # Populating the all categories into a dictionary 
            categories = {category.id:category.type for category in query}

            return jsonify({
                "success":True,
                "categories": categories,
            })
        except:
            abort(404)


    """
    @TODO:
    - Done Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            # Get all questions
            question_query = Question.query.order_by(Question.id).all()

            # Use pagination function to get required number of questions
            current_question = paginate_questions(question_query)

            category_query = Category.query.all()
            
            # Looping categories into a dictionary
            categories = {category.id:category.type for category in category_query}


            return jsonify({
                "success":True,
                "questions": current_question,
                "totalQuestions": len(question_query),
                "categories": categories,
                "currentCategory": None
            })
        except:
            abort(404)




    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            #  Getting question with selected id
            query = Question.query.filter_by(id=question_id).first()

            query.delete()

            return jsonify({
                "deleted": question_id,
                "success":True,
                "error":404
            })
        except:
            abort(422)




    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            body = request.get_json()

            if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
                abort(422)

            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_difficulty = body.get('difficulty', None)
            new_category = body.get('category', None)

            new_question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)

            new_question.insert()

            return jsonify({
                "success":True,
                "error":200
            })
        except:
            abort(422)



    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        try:
            body = request.get_json()

            if not 'searchTerm' in body:
                abort(404)

            search_term = body.get('searchTerm', None)

            search_result = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            questions = [question.format() for question in search_result]

            return jsonify({
                "success":True,
                "questions": questions,
                "totalQuestions":len(search_result),
                "currentCategory":None,
            })
        except:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def question_by_category(id):
        
        try:
            category = Category.query.filter_by(id=id).first()

            question_query = Question.query.filter_by(category=f'{category.id}').all()

            questions = [question.format() for question in question_query]

            return jsonify({
                "success": True,
                "questions":questions,
                "totalQuestions":len(question_query),
                "currentCategory": category.type
            })
            
        except:
            abort(404)
        


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()

            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')

            print(quiz_category['type'])

            if quiz_category['type'] == "click":
                query = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                query = Question.query.filter_by(category=quiz_category['id']).filter(
                Question.id.notin_(previous_questions)).all()


            question = query[random.randrange(0, len(query))].format()
            

            return jsonify({
                "question": question,
                "success":True,
            })
        except:
            abort(422)
    
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    #Error handlers

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message":"Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error":404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success":False,
            "error":405,
            "message":"Method Not Allowed"
        })

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success":False,
            "error": 422,
            "message":"Unprocessable Entity"
        }), 422

    return app


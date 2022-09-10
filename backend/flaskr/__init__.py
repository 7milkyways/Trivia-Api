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

            
            categories = {}
            # Populating the all categories into a dictionary 
            for category in query:
                categories[category.id] = category.type

            return jsonify({
                "success":True,
                "categories": categories,
            })
        except:
            abort(404)


    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            # Get all questions
            question_query = Question.query.order_by(Question.id).all()

            # Use pagination function to get required number of questions
            current_question = paginate_questions(question_query)

            category_query = Category.query.all()
            
            
            categories = {}
            # populating categories into a dictionary
            for category in category_query:
                categories[category.id] = category.type


            return jsonify({
                "success":True,
                "questions": current_question,
                "totalQuestions": len(question_query),
                "categories": categories,
            })
        except:
            abort(404)


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


    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            body = request.get_json()

            if not('searchTerm' in body):

                if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
                    abort(422)

                question = body.get('question')
                answer = body.get('answer')
                difficulty = body.get('difficulty')
                category = body.get('category')

                new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)

                new_question.insert()

                return jsonify({
                    "success":True,
                    "error":200
                })
            elif 'searchTerm' in body:
                search = body.get('searchTerm')
                
                query = Question.query.filter(Question.question.ilike(f'%{search}%')).all()

                search_result = paginate_questions(query)

                return jsonify({
                    "success":True,
                    "questions": search_result,
                    "totalQuestions":len(query),
                })
            else:
                abort(422)

        except:
            abort(422)

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def question_by_category(id):
        
        try:
            category = Category.query.filter_by(id=id).first()

            question_query = Question.query.filter_by(category=f'{category.id}').all()
            
            questions = []
            for question in question_query:
                questions.append(question.format())

            return jsonify({
                "success": True,
                "questions":questions,
                "totalQuestions":len(question_query),
                "currentCategory": category.type
            })
            
        except:
            abort(404)
        

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()

            # if not ('quiz_category' in body and 'previous_questions' in body):
            #     abort(404)

            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')

            if quiz_category['id'] == 0:
                query = Question.query.all()
            else:
                query = Question.query.filter_by(category=quiz_category['id']).all()
                
            question_length = len(query) - 1
            next_question = query[random.randrange(0, question_length)]
                
            if next_question.id not in previous_questions:
                next_question = query[random.randrange(0, question_length)]
                
                return jsonify({
                    "question": next_question.format(),
                    "success":True,
                })
            # else:
            #     next_question = query[random.randrange(0, question_length)]


        except:
            abort(422)

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


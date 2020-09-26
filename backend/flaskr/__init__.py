import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import randint

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def pagination(array, request, QUESTIONS_PER_PAGE):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    return array[start:end]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PATCH, OPTIONS')
    return response

  '''
  an endpoint to handle GET requests for categories. 
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    try:
      
      categories = [category.format() for category in Category.query.order_by(Category.id).all()]

      return jsonify({
        "success" : True, 
        "categories": categories,
        "total" : len(categories)
      })
    except:
      abort(500)

  '''
  an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''
  @app.route('/questions')
  def get_all_questions():
    try:
      questions = [question.format() for question in Question.query.order_by(Question.id).all()]
      categories = [category.format() for category in Category.query.order_by(Category.id).all()]

      questions_in_page = pagination(questions, request, QUESTIONS_PER_PAGE)

      if len(questions_in_page) == 0:
        abort(404)

      return jsonify({
          "success": True,
          "questions": questions_in_page,
          "categories": categories,
          "total_questions": len(questions)
      })
    except:
      abort(404)

  '''
  an endpoint to Search for question using a search term. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def get_questions():
    try:
      data = request.get_json()
      search_term = data.get('searchTerm', '')
      questions = [question.format() for question in Question.query.filter(Question.question.contains(search_term)).order_by(Question.id).all()]
      return jsonify({
          "success": True,
          "questions": pagination(questions, request, QUESTIONS_PER_PAGE),
          "total_questions": len(questions)
      })
    except:
      abort(500)

  '''
  an endpoint to DELETE question using a question ID. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.get(id)
      question.delete()    
      return jsonify({
          "success": True
      })
    except:
      abort(422)

  '''
  an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  '''
  @app.route('/questions', methods=['POST'])
  def new_questions():

    data = request.get_json()
    question = data.get('question', '')
    answer = data.get('answer', '')
    difficulty = data.get('difficulty', '')
    category = data.get('category', '')

    try:
      if (question == '') or (answer == '') or (difficulty == ''):
        abort(400)
      
      new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
      new_question.insert()

      return jsonify({
          "success": True
      })
      
    except:
      abort(400) 


  '''
  a GET endpoint to get questions based on category. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    try:
      questions = [question.format() for question in Question.query.filter(Question.category == id).order_by(Question.id).all()]
      return jsonify({
          "success": True,
          "questions": pagination(questions, request, QUESTIONS_PER_PAGE),
          "total_questions": len(questions),
      })
    except:
      abort(400)

  '''
  @TODO: 
  a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  '''
  @app.route('/quizzes', methods=["POST"])
  def get_quiz():
    try:
      data = request.get_json()
      previous_questions = data['previous_questions']
      quiz_category = data['quiz_category']

      questions = []

      if quiz_category["id"] != 0:
        questions = [question.format() for question in Question.query.filter(Question.category == quiz_category["id"]).all()]
      else: 
        questions = [question.format() for question in Question.query.all()]
      
      avaliable = []
      
      for question in questions:
        if question["id"] not in previous_questions:
          avaliable.append(question)

      if len(avaliable):  
        return jsonify({
            "success": True,
            "question": avaliable[randint(0, len(avaliable)-1)],
            "end": False
        })
      else:
        return jsonify({
            "success": True,
            "question": questions[0],
            "end": True
        })
    except:
      abort(400)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          'success': False,
          'error': 400,
          'message': 'Bad request error'
      }), 400
  
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          'success': False,
          'error': 404,
          'message': 'Resource not found'
      }), 404

  @app.errorhandler(422)
  def unprocesable_entity(error):
      return jsonify({
          'success': False,
          'error': 422,
          'message': 'Unprocessable entity'
      }), 422
  
  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({
          'success': False,
          'error': 500,
          'message': 'An error has occured, please try again'
      }), 500

  return app

    

import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  

  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  categories = Category.query.all()
  categories_formated = {category.id: category.type for category in categories  }  

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response


  
  @app.route('/categories', methods=['GET'])
  def categories():
    try:
      return jsonify({'success':True,
      'categories':categories_formated }), 200
    except:
      abort(400)

  def paginate(request, items):
    page = request.args.get('page', default= 1, type=int)
    start = (page -1)*10
    end = start+10
    items_on_apage = items[start:end]
    return items_on_apage
  

  @app.route('/questions', methods=['GET'])
  def questions():
    try:
      questions = Question.query.all()
      questions_formated = [question.format() for question in questions]
      questions_on_apage = paginate(request, questions_formated)
      if questions_on_apage:
        return jsonify({'success': True,
        'questions': questions_on_apage  ,
        'total_questions': len(questions_formated),
        'current_category': None,
        'categories': categories_formated 
        }), 200
      else:
        abort(404)
    except:
      abort(404)
      
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def questions_delete(id):
    question_delete = Question.query.filter(Question.id == id).one_or_none()
    if question_delete:
      db.session.delete(question_delete)
      db.session.commit()
      return jsonify({'success': True}), 200
    else:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions', methods=['POST'])
  def submit_question():
    try:
      question = request.get_json().get('question')
      answer = request.get_json().get('answer')
      difficulty = int(request.get_json().get('difficulty'))
      category_id = int(request.get_json().get('category'))
      added_question = Question(question= question, answer=answer, difficulty=difficulty, category=category_id)
      db.session.add(added_question)
      db.session.commit()
      return jsonify({'success': True}), 201
    except:
      abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions_search', methods=['POST'])
  def search_question():
    try:
      search_term = request.get_json().get('searchTerm')
      questions = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
      questions_formated = [question.format() for question in questions]
      return jsonify({'success': True,
      'questions': questions_formated,
      'total_questions': len(questions_formated)}), 200
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def catergories_question(id):
    try:
      selected_category = categories_formated[id]
      questions = Question.query.filter(Question.category==id).all()
      questions_formated = [question.format() for question in questions]
      return jsonify({'success': True,
      'questions': questions_formated,
      'total_questions': len(questions_formated ),
      'current_category': selected_category  }), 200
    except:
      abort(404)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quizzes():
    try:
      category_id = request.get_json().get('quiz_category')['id']
      prev_questions = request.get_json().get('previous_questions')
      quiz_question = Question.query.filter(~Question.id.in_(prev_questions), Question.category==category_id).first()
      return jsonify({'success': True,
      'question': quiz_question.format()})
    except:
      abort(400)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({'success': False,
    'error': 404,
    'message': 'Not Found :('  }), 404


  @app.errorhandler(422)
  def Unprocessable(error):
    return jsonify({'success': False,
    'error': 422,
    'message': 'Unprocessable :('  }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({'success': False,
    'error': 400,
    'message': 'Bad request :('  }), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({'success': False,
    'error': 405,
    'message': 'Method not allowed :('  }), 405

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({'success': False,
    'error': 500,
    'message': 'Server Error :('  }), 500
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    
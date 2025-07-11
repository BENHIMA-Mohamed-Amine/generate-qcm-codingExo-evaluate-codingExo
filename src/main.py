# build a flask app with two endpoints:
# 1. for generating qcm or code
# 2. for evaluating user code and providing feedback

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from .agents.eval_exo_agent import evaluate_and_feedback
from .services.generate_code_or_exo import generate_lab
import os
load_dotenv()

app = Flask(__name__)

# set up langsmith tracing for all the invocations
if 'LANGSMITH_API_KEY' in os.environ:
    os.environ['LANGSMITH_PROJECT'] = os.getenv('LANGSMITH_PROJECT', 'code-exercise-generation')
    os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGSMITH_API_KEY', 'your-api-key')
    os.environ['LANGSMITH_TRACING_V2'] = os.getenv('LANGSMITH_TRACING_V2', 'true')


@app.route('/')
def index():
    return "Welcome to the Code and Exercise Generation API!"


@app.route('/generate', methods=['POST'])
def generate_exercise():
    data = request.json
    context = data.get("context", "")
    number_of_questions = data.get("number_of_questions", 1)
    user_query = data.get("user_query", "")
    task = data.get("task", "qcm")
    difficulty = data.get("difficulty", "easy")

    try:
        results = generate_lab(context, number_of_questions, user_query, task, difficulty)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/evaluate', methods=['POST'])
def evaluate_exercise():
    data = request.json
    exercise = data.get("exercise", "")
    user_code = data.get("user_code", "")
    inputs = data.get("inputs", [])
    outputs = data.get("outputs", [])

    try:
        results = evaluate_and_feedback(exercise, user_code, inputs, outputs)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
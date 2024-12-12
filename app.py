from flask import Flask, render_template, request, jsonify
from datetime import datetime
from travel_crew import TravelCrew
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    context = {
        'message': message,
        'timestamp': datetime.now().isoformat()
    }

    try:
        crew = TravelCrew()
        result = crew.crew().kickoff(context)
        result = result.json
        return jsonify({'response': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 
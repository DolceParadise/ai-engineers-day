#!/usr/bin/env python
"""Quick test to verify Flask endpoint"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/ask', methods=['POST'])
def ask():
    return jsonify({
        "status": "success",
        "agents": [
            {"name": "TestAgent", "status": "complete", "output": "Test response", "tokens": {"prompt_tokens": 100, "completion_tokens": 50}}
        ],
        "final_answer": "Test complete",
        "token_summary": {"total_prompt_tokens": 100, "total_completion_tokens": 50, "total_cost_usd": 0.00025}
    })

if __name__ == '__main__':
    print("Starting test server on port 5001...")
    app.run(host='127.0.0.1', port=5001, debug=False)

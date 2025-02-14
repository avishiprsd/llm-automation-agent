from flask import Flask, request, jsonify
from app.tasks import execute_task, read_file

def create_app():
    app = Flask(__name__)

    @app.route("/run", methods=["POST"])
    def run_task():
        task = request.args.get("task")
        if not task:
            return jsonify({"error": "Task description required"}), 400
        try:
            result = execute_task(task)
            return jsonify({"result": result}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal Server Error"}), 500

    @app.route("/read", methods=["GET"])
    def read():
        path = request.args.get("path")
        content = read_file(path)
        if content is None:
            return "", 404
        return content, 200

    return app

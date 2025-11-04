from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import time
import os # Import os to check env variables

app = Flask(__name__)

# --- NEW: Check for test mode ---
IS_TEST_MODE = os.environ.get('TEST_MODE') == 'True'

if IS_TEST_MODE:
    # If in test mode, use a simple in-memory database
    print("Running in TEST_MODE: Using in-memory SQLite database.")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    # Original database configuration
    print("Running in Production/Development Mode: Connecting to MySQL.")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://myuser:mypassword@db/mydb'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}

# --- NEW: Health check route ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/users', methods=['POST'])
def create_user():
    name = request.json.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    name = request.json.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    user.name = name
    db.session.commit()
    return jsonify(user.to_dict())

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    # Updated startup logic
    with app.app_context():
        if IS_TEST_MODE:
            # For in-memory SQLite, just create all
            print("Creating in-memory database tables...")
            db.create_all()
            print("In-memory database ready.")
        else:
            # For MySQL, use the retry logic
            retries = 5
            while retries:
                try:
                    db.create_all()
                    print("Database tables created.")
                    break
                except Exception as e:
                    retries -= 1
                    print(f"Error connecting to database: {e}")
                    print(f"Retrying... ({retries} attempts left)")
                    time.sleep(5)
    
    # Run the app. Set debug=False for CI/Docker.
    app.run(host='0.0.0.0', port=5000, debug=False)
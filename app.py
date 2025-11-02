from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)

# Simple database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://myuser:mypassword@db/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}

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
    # Wait for database to be ready
    retries = 5
    while retries:
        try:
            with app.app_context():
                db.create_all()
                break
        except Exception as e:
            retries -= 1
            print(f"Error connecting to database, retrying... ({retries} attempts left)")
            time.sleep(5)
    
    app.run(host='0.0.0.0', debug=True)

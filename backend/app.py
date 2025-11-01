import os
from flask import Flask, send_from_directory, request, jsonify
from .database import db
from .models import User, Axiom

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder='../frontend')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'axiom_forge.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Placeholder for user management
def get_current_user():
    # For now, we'll create a user if one doesn't exist and always use user 1.
    user = User.query.get(1)
    if not user:
        user = User()
        db.session.add(user)
        db.session.commit()
    return user

@app.route('/api/axioms', methods=['GET'])
def get_axioms():
    user = get_current_user()
    axioms = Axiom.query.filter_by(user_id=user.id).all()
    return jsonify([{'id': axiom.id, 'text': axiom.text} for axiom in axioms])

@app.route('/api/axioms', methods=['POST'])
def add_axiom():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Axiom text is required'}), 400

    user = get_current_user()
    new_axiom = Axiom(text=data['text'], user_id=user.id)
    db.session.add(new_axiom)
    db.session.commit()

    return jsonify({'id': new_axiom.id, 'text': new_axiom.text}), 201

@app.route('/api/axioms/<int:axiom_id>', methods=['DELETE'])
def delete_axiom(axiom_id):
    axiom = Axiom.query.get(axiom_id)
    if not axiom:
        return jsonify({'error': 'Axiom not found'}), 404

    # In a real app, you'd also check if the axiom belongs to the current user

    db.session.delete(axiom)
    db.session.commit()

    return jsonify({'message': 'Axiom deleted successfully'})

from .dilemma_engine import generate_collaborative_dilemma, generate_red_team_dilemma

@app.route('/api/dilemma', methods=['POST'])
def get_dilemma():
    data = request.get_json()
    if not data or 'mode' not in data or 'axioms' not in data:
        return jsonify({'error': 'Mode and axioms are required'}), 400

    mode = data['mode']
    axioms = data['axioms']

    if mode == 'collaborative':
        if len(axioms) != 1:
            return jsonify({'error': 'Collaborative mode requires exactly one axiom'}), 400
        dilemma = generate_collaborative_dilemma(axioms[0])
    elif mode == 'red-team':
        if len(axioms) != 2:
            return jsonify({'error': 'Red-team mode requires exactly two axioms'}), 400
        dilemma = generate_red_team_dilemma(axioms[0], axioms[1])
    else:
        return jsonify({'error': 'Invalid mode specified'}), 400

    return jsonify(dilemma)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    """Serve static files from the 'frontend' directory."""
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True)

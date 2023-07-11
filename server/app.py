#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=['GET', 'POST'])
def scientist():
    if request.method == 'GET':
        scientists = Scientist.query.all()

        return [scientist.to_dict(rules=('-missions',)) for scientist in scientists], 200
    
    if request.method == 'POST':
        data = request.get_json()

        try:
            new_scientist = Scientist(
                name=data.get('name'),
                field_of_study=data.get('field_of_study')
            )

            db.session.add(new_scientist)
            db.session.commit()

            return new_scientist.to_dict(), 201
        
        except ValueError as e:
             return {'errors':['validation errors']}, 400


@app.route('/scientists/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def scientist_by_id(id):
    scientist = Scientist.query.filter_by(id=id).first()

    if not scientist:
        return {'error': 'Scientist not found'}, 404

    if request.method == 'GET':
        return scientist.to_dict(), 200
    
    if request.method == 'PATCH':
        data = request.get_json()
        try:
            for key in data:
                setattr(scientist, key, data[key])

            db.session.add(scientist)
            db.session.commit()

            return scientist.to_dict(rules=('-missions',)), 202
        
        except ValueError as e:
            return {'errors': ['validation errors']}, 400
    
    if request.method == 'DELETE':
        db.session.delete(scientist)
        db.session.commit()

        return {}, 204
    
@app.get('/planets')
def get_planets():
    
    planets = Planet.query.all()

    return [planet.to_dict(rules=('-missions',)) for planet in planets], 200

@app.post('/missions')
def add_mission():
    data = request.get_json()

    try:
        new_mission = Mission(
            name=data.get('name'),
            scientist_id=data.get('scientist_id'),
            planet_id=data.get('planet_id')
        )

        db.session.add(new_mission)
        db.session.commit()

        return new_mission.to_dict(), 201
    
    except ValueError as e:
        return {'errors': ['validation errors']}, 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)

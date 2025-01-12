from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', backref='planet', cascade='all, delete-orphan')

    # Add serialization rules
    serialize_rules = ('-missions.planet',)

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', backref='scientist', cascade='all, delete-orphan')

    # Add serialization rules
    serialize_rules = ('-missions.scientist', '-scientist.missions')

    # Add validation
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError('Must have name')
        return name
    
    @validates('field_of_study')
    def validate_field(self, key, field):
        if not field:
            raise ValueError('must input field')
        return field

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationships
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))

    # Add serialization rules
    serialize_rules = ('-scientist.missions', '-planet.missions')

    # Add validation
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError('must have name')
        return name
    
    @validates('scientist_id')
    def validate_scientist(self, key, scientist):
        if not scientist:
            raise ValueError('must have scientist id')
        return scientist
    
    @validates('planet_id')
    def validate_planet(self, key, planet):
        if not planet:
            raise ValueError('must have planet id')
        return planet
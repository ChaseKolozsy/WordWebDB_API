from flask import Blueprint, jsonify, request
from models import db, Object, Verb, Attribute, State, Routine
from sqlalchemy.exc import IntegrityError

objects = Blueprint('objects', __name__)

@objects.route('/schema')
def get_objects_schema():
    schema = {}
    for column in Object.__table__.columns:
        schema[column.name] = str(column.type)
    return jsonify(schema)

@objects.route('', methods=['GET'])
def get_all_objects():
    objects = Object.query_all()
    return jsonify([obj.to_dict() for obj in objects]), 200

@objects.route('/<int:object_id>', methods=['GET'])
def get_object(object_id):
    obj = Object.query_by_id(object_id)
    if obj:
        return jsonify(obj.to_dict()), 200
    return jsonify({'error': 'Object not found'}), 404

@objects.route('/<string:object_name>', methods=['GET'])
def get_object_by_name(object_name):
    obj = Object.query_by_name(object_name)
    if obj:
        return jsonify(obj.to_dict()), 200
    return jsonify({'error': 'Object not found'}), 404

@objects.route('', methods=['POST'])
def create_object():
    data = request.get_json()
    obj = Object(name=data.get('name'))
    try:
        obj.add()
        return jsonify(obj.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Integrity error, possibly duplicate entry'}), 400

@objects.route('/<int:object_id>', methods=['PUT'])
def update_object(object_id):
    data = request.get_json()
    obj = Object.query_by_id(object_id)
    if obj:
        obj.update(name=data.get('name'))
        return jsonify(obj.to_dict()), 200
    return jsonify({'error': 'Object not found'}), 404

@objects.route('/<int:object_id>', methods=['DELETE'])
def delete_object(object_id):
    obj = Object.query_by_id(object_id)
    if obj:
        obj.delete()
        return jsonify({'message': 'Object deleted'}), 200
    return jsonify({'error': 'Object not found'}), 404

@objects.route('/<int:object_id>/add_association', methods=['POST'])
def add_association(object_id):
    data = request.get_json()
    obj = Object.query_by_id(object_id)
    if not obj:
        return jsonify({'error': 'Object not found'}), 404

    assoc_type = data.get('type')
    assoc_id = data.get('id')

    if assoc_type == 'verb':
        assoc_obj = Verb.query_by_id(assoc_id)
        if assoc_obj:
            obj.verbs.append(assoc_obj)
        else:
            return jsonify({'error': 'Verb not found'}), 404
    elif assoc_type == 'attribute':
        assoc_obj = Attribute.query_by_id(assoc_id)
        if assoc_obj:
            obj.attributes.append(assoc_obj)
        else:
            return jsonify({'error': 'Attribute not found'}), 404
    elif assoc_type == 'state':
        assoc_obj = State.query_by_id(assoc_id)
        if assoc_obj:
            obj.states.append(assoc_obj)
        else:
            return jsonify({'error': 'State not found'}), 404
    elif assoc_type == 'routine':
        assoc_obj = Routine.query_by_id(assoc_id)
        if assoc_obj:
            obj.routines.append(assoc_obj)
        else:
            return jsonify({'error': 'Routine not found'}), 404
    else:
        return jsonify({'error': 'Invalid association type'}), 400

    db.session.commit()
    return jsonify(obj.to_dict()), 200

@objects.route('/query_by_association', methods=['POST'])
def query_by_association():
    data = request.get_json()
    assoc_type = data.get('type')
    assoc_id = data.get('id')

    if assoc_type == 'verb':
        objects = Object.query.join(Object.verbs).filter(Verb.verb_id == assoc_id).all()
    elif assoc_type == 'attribute':
        objects = Object.query.join(Object.attributes).filter(Attribute.attribute_id == assoc_id).all()
    elif assoc_type == 'state':
        objects = Object.query.join(Object.states).filter(State.state_id == assoc_id).all()
    elif assoc_type == 'routine':
        objects = Object.query.join(Object.routines).filter(Routine.routine_id == assoc_id).all()
    else:
        return jsonify({'error': 'Invalid association type'}), 400

    return jsonify([obj.to_dict() for obj in objects]), 200

@objects.route('/<int:object_id>/remove_association', methods=['POST'])
def remove_association(object_id):
    data = request.get_json()
    obj = Object.query_by_id(object_id)
    if not obj:
        return jsonify({'error': 'Object not found'}), 404

    assoc_type = data.get('type')
    assoc_id = data.get('id')

    if assoc_type == 'verb':
        assoc_obj = Verb.query_by_id(assoc_id)
        if assoc_obj and assoc_obj in obj.verbs:
            obj.verbs.remove(assoc_obj)
        else:
            return jsonify({'error': 'Verb not found or not associated'}), 404
    elif assoc_type == 'attribute':
        assoc_obj = Attribute.query_by_id(assoc_id)
        if assoc_obj and assoc_obj in obj.attributes:
            obj.attributes.remove(assoc_obj)
        else:
            return jsonify({'error': 'Attribute not found or not associated'}), 404
    elif assoc_type == 'state':
        assoc_obj = State.query_by_id(assoc_id)
        if assoc_obj and assoc_obj in obj.states:
            obj.states.remove(assoc_obj)
        else:
            return jsonify({'error': 'State not found or not associated'}), 404
    elif assoc_type == 'routine':
        assoc_obj = Routine.query_by_id(assoc_id)
        if assoc_obj and assoc_obj in obj.routines:
            obj.routines.remove(assoc_obj)
        else:
            return jsonify({'error': 'Routine not found or not associated'}), 404
    else:
        return jsonify({'error': 'Invalid association type'}), 400

    db.session.commit()
    return jsonify(obj.to_dict()), 200
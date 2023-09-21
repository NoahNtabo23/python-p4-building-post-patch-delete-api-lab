#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():

    bakeries = Bakery.query.all()
    bakeries_serialized = [bakery.to_dict() for bakery in bakeries]

    response = make_response(
        bakeries_serialized,
        200
    )
    return response

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()
    bakery_serialized = bakery.to_dict()

    response = make_response(
        bakery_serialized,
        200
    )
    return response

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get("name")
    price = request.form.get("price")
    bakery_id = request.form.get("id")
    
    if not name or not price or not bakery_id:
        return make_response(jsonify({'error': 'Name, price, and bakery_id are required.'}), 400)

    existing_good = BakedGood.query.filter_by(name=name).first()
    if existing_good:
        return make_response(jsonify({'error': 'A baked good with this name already exists.'}), 400)

    new_good = BakedGood(
        name=name,
        price=price,
        bakery_id=bakery_id
    )
    db.session.add(new_good)
    db.session.commit()

    return jsonify({
        'name': new_good.name,
        'price': new_good.price,
        'bakery_id': new_good.bakery_id
    }), 201

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get(id)
    
    if not bakery:
        return make_response(jsonify({'error': 'Bakery not found.'}), 404)
    
    data = request.form
    name = data.get('name')
    
    if name:
        bakery.name = name
    
    db.session.commit()
    
    return make_response(jsonify(bakery.to_dict()), 200)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    
    if not baked_good:
        return make_response(jsonify({'error': 'Baked good not found.'}), 404)
    
    db.session.delete(baked_good)
    db.session.commit()
    
    return make_response(jsonify({'message': 'Baked good deleted successfully.'}), 200)



@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    
    response = make_response(
        baked_goods_by_price_serialized,
        200
    )
    return response

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()

    response = make_response(
        most_expensive_serialized,
        200
    )
    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)

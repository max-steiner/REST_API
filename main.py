from refresh_db import refresh_db
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import Flask, request, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from db_repo import DbRepo
from db_config import local_session
from customer import Customer
from logger import Logger

# application config
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
repo = DbRepo(local_session)
logger = Logger.get_instance()
refresh_db()


def convert_to_json(_list: list):
    json_list = []
    for i in _list:
        _dict = i.__dict__
        _dict.pop('_sa_instance_state', None)
        json_list.append(_dict)
    return json_list


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            token = token.removeprefix('Bearer ')
        if not token:
            logger.logger.info('User token is incorrect.')
            return jsonify({'message': 'User token is incorrect'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            customer = repo.get_customer_by_id(data['id'])
        except:
            logger.logger.warning('User token is invalid.')
            return jsonify({'message': 'User token is invalid'}), 401
        return f(customer, *args, **kwargs)
    return decorated


# URL - handlers
@app.route("/")
def home():
    return '''
        <html>
            Welcome to Max Steiner REST API Project!
        </html>
    '''


@app.route('/customers', methods=['GET', 'POST'])
@token_required
def get_or_post_customer():
    if request.method == 'GET':
        customers = repo.get_all_customers()
        output = []
        for customer in customers:
            output.append({'id': customer.id, 'username': customer.username, 'password': customer.password,
                           'email': customer.email, 'address': customer.address})
        return jsonify({'customers': output})
    if request.method == 'POST':
        new_customer = request.get_json()
        insert_customer = Customer(username=new_customer["username"], password=new_customer["password"],
                                   email=new_customer["email"], address=new_customer["address"])
        repo.add_new_customer(insert_customer)
        logger.logger.info(f'New customer: {insert_customer} has been created!')
        return make_response('New customer created!', 201)
    return repo.get_all_customers()


@app.route('/customers/<int:id>', methods=['GET', 'PUT', 'DELETE', 'PATCH'])
@token_required
def get_customer_by_id(id):
    if request.method == 'GET':
        customer = repo.get_customer_by_id(id)
        return jsonify({'id': customer.id, 'username': customer.username, 'password': customer.password,
                        'email': customer.email, 'address': customer.address})
    if request.method == 'PUT':
        new_customer = request.get_json()
        back = repo.update_put_customer(id, new_customer)
        if back:
            logger.logger.info(f'The customer with the id: {id} has been updated!')
            return make_response('The customer has been update by PUT', 201)
        else:
            logger.logger.error(f'Could not update the customer with the id: {id}')
            return jsonify({'answer': 'failed'})
    if request.method == 'PATCH':
        new_customer = request.get_json()
        back = repo.update_patch_customer(id, new_customer)
        if back:
            logger.logger.info(f'The customer with the id: {id} has been updated!')
            return make_response('The customer has been updated by PATCH.', 201)
        else:
            logger.logger.error(f'Could not update the customer with the id: {id}')
            return jsonify({'answer': 'failed'})
    if request.method == 'DELETE':
        back = repo.delete_customer(id)
        if back:
            logger.logger.info(f'The customer with the id: {id} has been deleted!')
            return make_response('The customer has been deleted', 201)
        else:
            logger.logger.error(f'Could not delete a customer with the id: {id}')
            return jsonify({'answer': 'failed'})


@app.route('/signup', methods=['POST'])
def signup():
    form_data = request.form
    username = form_data.get('username')
    password = form_data.get('password')
    email = form_data.get('email')
    address = form_data.get('address')
    customer = repo.get_customer_by_username(username)
    if customer:
        logger.logger.error(f'Username already exists')
        return make_response('Username already exists', 202)
    else:
        insert_customer = Customer(id=None, username=username, password=generate_password_hash(password),
                                   email=email, address=address)
    if insert_customer:
        repo.add_new_customer(insert_customer)
        logger.logger.info(f'New customer: {insert_customer} has been created')
        return make_response('New customer created', 201)
    else:
        logger.logger.error('Incorrect data.')
        return jsonify({'answer': 'failed'})


@app.route('/login', methods=['POST'])
def login():
    form_data = request.form
    if not form_data or not form_data.get("username") or not form_data.get("password"):
        logger.logger.info('Incorrect data for customer: username, password')
        return make_response('Customer not verified', 401)
    customer = repo.get_customer_by_username(form_data.get('username'))
    if not customer:
        logger.logger.warning(f'Customer username not verified')
        return make_response('Customer username not verified', 401)
    if not check_password_hash(customer.password, form_data.get("password")):
        logger.logger.error(f'Customer password not verified.')
        return make_response('Customer password not verified', 401)
    logger.logger.debug(f'The user: {form_data.get("username")} logged in successfully!')
    token = jwt.encode({'public_id': customer.id, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                       app.config['SECRET_KEY'])
    print(token)
    return make_response(jsonify({'token': token}), 201)


if __name__ == '__main__':
    app.run(debug=False)

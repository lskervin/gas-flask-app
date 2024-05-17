import csv
from flask_restful import Resource
from models import User, PaymentMethod, Order, Driver
from flask import Flask, make_response, request, session
from datetime import datetime, date
from config import app, db, api, bcrypt
from flask_cors import CORS
import requests
import stripe
import os
from bs4 import BeautifulSoup
import us
import re
from dotenv import load_dotenv

load_dotenv()
# Instantiate CORS
CORS(app, supports_credentials=True)

@app.route('/')
def home():
    return ''


class Login(Resource):
    def post(self):
        json_data = request.get_json()
        email = json_data.get('email')
        password = json_data.get('password')
        
        if not email or not password:
            return {'error': 'email and password are required'}, 400
        
        user = User.query.filter_by(email=email).first()
        driver = Driver.query.filter_by(email=email).first()

        if not user or driver:
            return {'error': 'user not found'}, 404
        
        if user:
            user.authenticate(password=password)
            # Store user id in session
            session['user_id'] = user.id
            return user.to_dict(), 200
        elif driver:
            driver.authenticate(password=password)
            # Store driver id in session
            session['driver_id'] = driver.id
            return driver.to_dict(), 200
        else:
            return {'error': 'login failed'}, 401
  
class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        session.pop('driver_id', None)
        return {}, 204
    
class Signup(Resource):
    def post(self):
        json_data = request.get_json()
        email = json_data.get('email')

        existing_user = User.query.filter_by(email=email).first()
        existing_driver = Driver.query.filter_by(email=email).first()

        if existing_user or existing_driver:
            return {'error': 'email already exists'}, 400

        # Check if the request is for creating a user or a driver
        if 'driver' in json_data:
            # Create a new driver
            new_driver = Driver(
                first_name=json_data.get('first_name'),
                last_name=json_data.get('last_name'),
                cell_number=json_data.get('cell_number'),
                license_no=json_data.get('license_no'),
                _ssn=json_data.get('_ssn'),
                license_plate=json_data.get('license_plate'),
                mailing_address=json_data.get('mailing_address'),
                email=email,
                _password=json_data.get('_password')
            )
            db.session.add(new_driver)
            db.session.commit()
            session['driver_id'] = new_driver.id
            return new_driver.to_dict(), 201
        else:
            # Create a new user
            new_user = User(
                first_name=json_data.get('first_name'),
                last_name=json_data.get('last_name'),
                mailing_address=json_data.get('mailing_address'),
                cell_number=json_data.get('cell_number'),
                email=email,
                _password=bcrypt.generate_password_hash('_password').decode('utf-8'),
            )

            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return new_user.to_dict(), 201

class CheckUserSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if user_id:
            user = User.query.get(user_id)
            return make_response(user.to_dict(), 200)
        else:
            return make_response({'error': 'unauthorized'}, 401)

class CheckDriverSession(Resource):
    def get(self):
        driver_id = session.get('driver_id')
        
        if driver_id:
            driver = Driver.query.get(driver_id)
            return driver.to_dict(), 200
        else:
            return {'error': 'unauthorized'}, 401

class UserResource(Resource):

    def get(self, user_id=None):
        if user_id is not None:
            user = User.query.filter(User.id == user_id).one_or_none()
            if user:
                return make_response(user.to_dict(), 200)
            else:
                return {'error': 'User not found'}, 404
        else:
            users = [user.to_dict() for user in User.query.all()]
            return make_response(users, 200)
    
    def post(self):
        # Implement logic to create a new user
        fields = request.get_json()
        try:
            user = User(
                email=fields['email'],
                _password=fields['_password'],
            )
            db.session.add(user)
            db.session.commit()
            return make_response(user.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
    
    def patch(self, user_id):
        # Implement logic to update user by ID
        user = User.query.filter(User.id == user_id).one_or_none()

        if user is None:
            return make_response({'error': 'User not found'}, 404)
    
        fields = request.get_json()
        try:
            for field in fields:
                setattr(user, field, fields[field])
            db.session.commit()

            return make_response(user.to_dict(), 202)

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
        
    def delete(self, user_id):
        user = User.query.filter(User.id == user_id).one_or_none()

        if user is None:
            return make_response({'error': 'User not found'}, 404)
        db.session.delete(user)
        db.session.commit()
        return make_response({}, 204)

class DriverResource(Resource):

    def get(self, driver_id=None):
        if driver_id is not None:
            driver = Driver.query.filter(Driver.id == driver_id).one_or_none()
            if driver:
                return make_response(driver.to_dict(), 200)
            else:
                return {'error': 'User not found'}, 404
        else:
            drivers = [driver.to_dict() for driver in Driver.query.all()]
            return make_response(drivers, 200)
    
    def post(self):
        # Implement logic to create a new driver
        fields = request.get_json()
        try:
            driver = Driver(

                first_name=fields['first_name'],
                last_name=fields['last_name'],
                cell_number=fields['cell_number'],
                license_no=fields['license_no'],
                _ssn=fields['_ssn'],
                license_plate=fields['license_plate'],
                mailing_address=fields['mailing_address'],
                email=fields['email'],
                _password=fields['_password']

            )
            db.session.add(driver)
            db.session.commit()
            return make_response(driver.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
    
    def patch(self, driver_id):
        # Implement logic to update driver by ID
        driver = Driver.query.filter(Driver.id == driver_id).one_or_none()

        if driver is None:
            return make_response({'error': 'User not found'}, 404)
    
        fields = request.get_json()
        try:
            for field in fields:
                setattr(driver, field, fields[field])
            db.session.commit()

            return make_response(driver.to_dict(), 202)

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
        
    def delete(self, driver_id):
        driver = Driver.query.filter(Driver.id == driver_id).one_or_none()

        if driver is None:
            return make_response({'error': 'User not found'}, 404)
        db.session.delete(driver)
        db.session.commit()
        return make_response({}, 204)

class OrderResource(Resource):
    def get(self, order_id=None):
        if order_id:
            order = Order.query.get(order_id)
            if order:
                return order.to_dict(), 200
            else:
                return {'error': 'Order not found'}, 404
        else:
            orders = Order.query.all()
            return [order.to_dict() for order in orders], 200

    def post(self):
        json_data = request.get_json()
        new_order = Order(
            user_id=json_data['user_id'],
            fuel_type=json_data['fuel_type'],
            quantity=json_data['quantity'],
            ppg=json_data['ppg'],
            total=json_data['total'],
            total_payout=json_data['total_payout'],
            license_plate=json_data['license_plate'],
            order_location=json_data['order_location']
        )
        db.session.add(new_order)
        db.session.commit()
        return new_order.to_dict(), 201

    def patch(self, order_id):
        json_data = request.get_json()
        order = Order.query.get(order_id)
        if not order:
            return {'error': 'Order not found'}, 404
        for key, value in json_data.items():
            setattr(order, key, value)
        db.session.commit()
        return order.to_dict(), 200

    def delete(self, order_id):
        order = Order.query.get(order_id)
        if not order:
            return {'error': 'Order not found'}, 404
        db.session.delete(order)
        db.session.commit()
        return {'message': 'Order deleted successfully'}, 200

class CarData(Resource):
    def get(self, license_plate):
        with open('license_plate_validator.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['License_Plate'] == license_plate:
                    return row, 200
        return {'message': 'License plate not found'}, 404

class GasStations(Resource):
    def get(self, zipCode):
        try:
            # Construct the URL
            url = f'https://www.autoblog.com/{zipCode}-gas-prices/'

            # Send a GET request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all <li> elements containing the gas station info
            li_shops = soup.find_all('li', class_='name')

            gas_stations = []
            for li in li_shops:
                # Extract gas station details
                shop_name = li.find('h4').get_text(strip=True)
                shop_address = li.find('address').get_text(strip=True)
                href = li.find('a').get('href')

                # Scrape gas prices using the href URL
                gas_prices = self.scrape_gas_prices(href)

                gas_stations.append({'name': shop_name, 'address': shop_address, 'prices': gas_prices})

            # Calculate average gas prices
            average_prices = self.calculate_average_prices(gas_stations)

            if average_prices:
                return {'average_prices': average_prices, 'gas_stations': gas_stations}, 200
            else:
                return {'error': 'No gas prices found'}, 404

        except Exception as e:
            return {'error': str(e)}, 500

    def scrape_gas_prices(self, href):
        try:
            # Send a GET request to the gas station URL
            response = requests.get(href)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the <dl> element containing the gas prices
            dl_prices = soup.find('dl', class_='gas-prices')

            gas_prices = {}
            if dl_prices:
                # Extract gas prices
                for dt, dd in zip(dl_prices.find_all('dt'), dl_prices.find_all('dd')):
                    gas_prices[dt.get_text(strip=True)] = float(dd.get_text(strip=True).replace('$', ''))

            return gas_prices
        except Exception as e:
            print(f"Error scraping gas prices: {e}")
            return {}

    def calculate_average_prices(self, gas_stations):
        # Initialize dictionary to store sum of prices for each grade
        sum_prices = {}
        # Initialize dictionary to store count of gas stations for each grade
        count_stations = {}
        # Iterate over gas stations
        for station in gas_stations:
            prices = station['prices']
            # Iterate over gas prices for each station
            for grade, price in prices.items():
                if grade in sum_prices:
                    sum_prices[grade] += price
                    count_stations[grade] += 1
                else:
                    sum_prices[grade] = price
                    count_stations[grade] = 1
        
        # Calculate average prices
        average_prices = {}
        for grade, total_price in sum_prices.items():
            count = count_stations[grade]
            average_price = total_price / count
            # Round the average price to 4 decimal places
            average_prices[grade] = round(average_price, 4)

        return average_prices

stripe.api_key = os.environ['STRIPE_API_KEY']

class PaymentAuthentication(Resource):
    def post(self):
        try:
            # Get the payment token from the request data
            token = request.json['token']

            # Create a PaymentIntent using the Stripe API
            intent = stripe.PaymentIntent.create(
                amount=1000,  # Amount in cents (e.g., $10.00)
                currency='usd',
                payment_method_types=['card'],
                payment_method=token,
                confirm=True,
            )

            # If PaymentIntent creation is successful, return client secret
            return {'clientSecret': intent.client_secret}

        except stripe.error.CardError as e:
            # If the card is declined, return error message
            return {'status': 'error', 'message': str(e)}, 400


# Add resources to the API with corresponding routes
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Signup, '/signup')
api.add_resource(CheckUserSession, '/check_user_session')
api.add_resource(CheckDriverSession, '/check_driver_session')
api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(DriverResource, '/drivers', '/drivers/<int:driver_id>')
api.add_resource(OrderResource, '/orders', '/orders/<int:order_id>')
api.add_resource(CarData, '/car/<string:license_plate>')
api.add_resource(GasStations, '/gas-stations/<string:zipCode>/')
api.add_resource(PaymentAuthentication, '/payment/authenticate')

if __name__ == '__main__':
    app.run(port=8000, debug=True)
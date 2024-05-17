from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime
from config import db, bcrypt


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    cell_number = db.Column(db.String(15), nullable=True)
    mailing_address = db.Column(db.String, nullable=True)
    _cars = db.Column(db.JSON, nullable=True)
    current_location = db.Column(db.String(), nullable=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    _password = db.Column(db.String, nullable=False)


    # Relationship with PaymentMethod
    payment_methods = db.relationship('PaymentMethod', back_populates='user')

    orders = db.relationship('Order', back_populates='user')

    serialize_rules = ('-orders.user_id', '-orders.user','-payment_methods.user_id','-payment_methods.user')

    def __repr__(self):
        return f'<User {self.first_name} {self.last_name}>'


    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, new_password):
        pass_hash = bcrypt.generate_password_hash(new_password.encode('utf-8'))
        self._password = pass_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password, password.encode('utf-8'))
    
    @property
    def cars(self):
        if self._cars:
            return self._cars.split(',')  # Split the string into a list
        else:
            return []

    @cars.setter
    def cars(self, cars):
        if cars:
            self._cars = ','.join(cars)  # Join the list into a comma-separated string
        else:
            self._cars = None


class PaymentMethod(db.Model, SerializerMixin):
    __tablename__ = 'payment_methods'

    id = db.Column(db.Integer, primary_key=True)
    _card_number = db.Column(db.String, nullable=False)  # Increased size to accommodate hashed value
    card_number_last_4 = db.Column(db.String(4), nullable=False)
    _cvv = db.Column(db.String, nullable=False)  # Increased size to accommodate hashed value
    expiration_date = db.Column(db.String(5), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='payment_methods')

    serialize_rules = ('-user_id', '-user')

    def __repr__(self):
        return f'<PaymentMethod {self._card_number}>'
    
    @hybrid_property
    def card_number(self):
        return self._card_number
    
    @card_number.setter
    def card_number(self, card_number):
        # Hash the card number
        hashed = bcrypt.generate_password_hash(card_number.encode('utf-8'))
        self._card_number = hashed.decode('utf-8')
        
        # Only store the last 4 digits separately
        self.card_number_last_4 = card_number[-4:]

    def authenticate(self, card_number):
        return bcrypt.check_password_hash(self._card_number, card_number.encode('utf-8'))

    @hybrid_property
    def cvv(self):
        return self._cvv

    @cvv.setter
    def cvv(self, value):
        pass_hash = bcrypt.generate_password_hash(value.encode('utf-8'))
        self._cvv = pass_hash.decode('utf-8')

    def authenticate(self, value):
        return bcrypt.check_password_hash(self._cvv, value.encode('utf-8'))

class Driver(db.Model, SerializerMixin):
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    cell_number = db.Column(db.String(15), nullable=False)
    license_no = db.Column(db.String, nullable=False)
    _ssn = db.Column(db.String, nullable=False)  # Increased size to accommodate hashed value
    ssn_last_4 = db.Column(db.String(4), nullable=False)
    license_plate = db.Column(db.String, nullable=False)
    mailing_address = db.Column(db.String, nullable=False)
    current_location = db.Column(db.String(), nullable=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    _password = db.Column(db.String, nullable=False)

    #relationship with orders
    orders = db.relationship('Order', back_populates='driver')

    serialize_rules = ('-orders.driver_id', '-orders.driver')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, new_password):
        pass_hash = bcrypt.generate_password_hash(new_password.encode('utf-8'))
        self._password = pass_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password, password.encode('utf-8'))
    
    @hybrid_property
    def ssn(self):
        return self._ssn
    
    @ssn.setter
    def ssn(self, ssn):
        # Hash the card number
        hashed = bcrypt.generate_password_hash(ssn.encode('utf-8'))
        self._ssn = hashed.decode('utf-8')
        
        # Only store the last 4 digits separately
        self.ssn_last_4 = ssn[-4:]

    def authenticate(self, ssn):
        return bcrypt.check_password_hash(self._ssn, ssn.encode('utf-8'))

class Order(db.Model, SerializerMixin):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='created')
    fuel_type = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Number of gals ordered
    ppg = db.Column(db.Float, nullable=False)  # ppg
    total = db.Column(db.Float, nullable=False)  # Total price of the order
    total_payout= db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    license_plate = db.Column(db.String, nullable=False)
    order_location= db.Column(db.String, nullable=False)

    user = db.relationship('User', back_populates='orders')
    driver = db.relationship('Driver', back_populates='orders')

    serialize_rules = ('-user_id','-user')

    def __repr__(self):
        return f'<Order {self.id}>'


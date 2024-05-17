from datetime import datetime
from config import app, db, bcrypt
from models import User, PaymentMethod, Order

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Create sample data for users
        user1 = User(
            first_name='John',
            last_name='Doe',
            cell_number='123456789',
            email='john@example.com',
            password=bcrypt.generate_password_hash('password').decode('utf-8'),
        )

        db.session.add(user1)
        db.session.commit()

        # Create sample data for payment methods
        payment_method1 = PaymentMethod(
            card_number='1234567890123456',
            expiration_date='12/25',
            cvv='123',
            postal_code='12345',
            user=user1
        )

        # Create sample data for orders
        order1 = Order(
            user=user1,
            status='created',
            fuel_type='93',
            quantity=15,
            ppg=6.5410,
            total=94.79,
            total_payout=5.42,
            timestamp=datetime.now(),
            license_plate='LGE5082Y',
            order_location='201-17 100th Avenue, Hollis, NY, USA'
        )

        # Add instances to the session and commit changes
        db.session.add(payment_method1)
        db.session.add(order1)
        db.session.commit()

if __name__ == "__main__":
    seed_data()
    print("Sample data has been seeded successfully.")

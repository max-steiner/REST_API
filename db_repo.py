from sqlalchemy.exc import OperationalError
from logger import Logger
from customer import Customer


class DbRepo:
    """Special class for database maintenance"""

    def __init__(self, local_session):
        self.local_session = local_session
        self.logger = Logger.get_instance()

    def reset_auto_inc(self, table_class):
        self.local_session.execute(f'TRUNCATE TABLE {table_class.__tablename__} RESTART IDENTITY CASCADE')

    def delete_table(self):
        self.local_session.execute(f'drop TABLE if exists Customer')
        self.local_session.commit()

    def add_new_customer(self, new_customer):
        if not isinstance(new_customer, Customer):
            self.logger.logger.error(
                f'Function <<add_new_customer>> failed: invalid class Customer.'
                )
            return False
        if not hasattr(new_customer, "username") or not hasattr(new_customer, "password"):
            self.logger.logger.error(
                f'Function <<add_new_customer>> failed: invalid data(username or password).'
            )
            return False
        if not hasattr(new_customer, "email") or not hasattr(new_customer, "address"):
            self.logger.logger.error(
                f'Function <<add_new_customer>> failed: invalid data(email or address).'
            )
            return False
        try:
            self.local_session.add(new_customer)
            self.local_session.commit()
            self.logger.logger.info(
                f'The new customer {new_customer} has been added to the database'
            )
        except OperationalError as exc:
            self.logger.logger.critical(
                f'The function <<add_new_customer>> failed: {exc}'
                f'The customer {new_customer} has not been added to the database'
            )

    def delete_customer(self, id_):
        try:
            self.local_session.query(Customer).filter(Customer.id == id_).delete(synchronize_session=False)
            self.local_session.commit()
            self.logger.logger.info(
                f'The customer with ID {id_} has been deleted from database')
            return True
        except OperationalError as exc:
            self.logger.logger.error(
                f'The function <<delete_customer_by_id>> failed: {exc}'
            )

    def get_all_customers(self):
        try:
            all_customers = self.local_session.query(Customer).all()
            self.logger.logger.info(
                f'The function <<get_all_customers>> successfully completed')
            return all_customers
        except OperationalError as exc:
            self.logger.logger.error(
                f'The function <<get_all_customers>> failed: {exc}'
            )

    def get_customer_by_id(self, id_):
        try:
            customer = self.local_session.query(Customer).get(id_)
            self.logger.logger.info(
                f'The function <<get_customers_by_id>> successfully completed. ID: {id_}')
            return customer
        except OperationalError as exc:
            self.logger.logger.error(
                f'The function <<get_customer_by_id>> failed: {exc}'
            )

    def update_put_customer(self, id_, values):
        updated_values = {}
        for key, value in values.items():
            if key == 'username' or key == 'password' or key == 'email' or key == 'address':
                updated_values[key] = value
        if len(list(updated_values.keys())) == 4:
            customer = Customer(username=updated_values["username"], password=updated_values["password"],
                                email=updated_values["email"], address=updated_values["address"])
            self.local_session.query(Customer).filter(Customer.id == id_).update(customer)
            self.local_session.commit()
            self.logger.logger.info(
                f'The function <<update_put_customer>> successfully completed. ID: {id_}')
            return True
        else:
            self.logger.logger.error(
                f'The function <<update_put_customer>> failed. ID: {id_}')
            return False

    def update_patch_customer(self, id_, values):
        updated_values = {}
        for key, value in values.items():
            if key == 'username' or key == 'password' or key == 'email' or key == 'address':
                updated_values[key] = value
        if len(list(updated_values.keys())) == 4:
            customer = Customer(username=updated_values["username"], password=updated_values["password"],
                                email=updated_values["email"], address=updated_values["address"])
            try:
                self.local_session.query(Customer).filter(Customer.id == id_).update(customer)
                self.local_session.commit()
            except OperationalError as a:
                self.logger.logger.critical(a)
        else:
            customer = self.local_session.query(Customer).get(id_)
            if 'username' in updated_values:
                username = updated_values["username"]
            else:
                username = customer.username
            if 'password' in updated_values:
                password = updated_values["password"]
            else:
                password = customer.password
            if 'email' in updated_values:
                email = updated_values["email"]
            else:
                email = customer.email
            if 'address' in updated_values:
                address = updated_values["address"]
            else:
                address = customer.address
            new_customer = Customer(username=username, password=password, email=email, address=address)
            try:
                self.local_session.query(Customer).filter(Customer.id == id_).update(new_customer)
                self.local_session.commit()
                self.logger.logger.info(
                    f'The function <<update_patch_customer>> successfully completed. ID: {id_}')
            except OperationalError as a:
                self.logger.logger.critical(a)

    def get_customer_by_username(self, username):
        customer = self.local_session.query(Customer).filter(Customer.username == username).all()
        if customer:
            self.logger.logger.info(
                f'The function <<get_customers_by_username>> successfully completed. Username: {username}')
            return customer[0]
        else:
            self.logger.logger.info(
                f'The function <<get_customers_by_username>> failed. Username: {username}')
        return False

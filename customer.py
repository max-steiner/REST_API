from sqlalchemy import Column, String, BigInteger
from db_config import Base


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(BigInteger(), primary_key=True, nullable=False, autoincrement=True)
    username = Column(String(), nullable=False, unique=True)
    password = Column(String(), nullable=False)
    email = Column(String(), nullable=False, unique=True)
    address = Column(String(), nullable=False)

    def __repr__(self):
        return f'''Customer id: {self.id}, 
                username: {self.username}, 
                password: {self.password}, 
                email: {self.email},
                address: {self.address}'''

    def __str__(self):
        return f'''Customer id: {self.id}, 
                username: {self.username}, 
                password: {self.password}, 
                email: {self.email},
                address: {self.address}'''

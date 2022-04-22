from db_config import local_session, create_all_entities
from db_repo import DbRepo
from customer import Customer
from logger import Logger


repo = DbRepo(local_session)


def refresh_db():   # helper function to restart the database
    repo.reset_auto_inc(Customer)
    repo.delete_table()
    create_all_entities()
    logger = Logger.get_instance()
    logger.logger.critical('The data base  has been successfully refreshed')




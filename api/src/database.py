import sqlalchemy as sa
from sqlalchemy.orm import registry, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from .settings import database_settings as settings
from .logger import LoggerHandler, get_logger, logger


class DatabaseInterface:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self, only_registry: bool = False):
        """
        Initialize the database connection
        """
        if not hasattr(self, 'initialized'):
            if only_registry:
                self.tables_registry = registry()
            else:
                self.create_instance()
            self.initialized = True

    def create_instance(self):
        """
        Create a new instance of the database connector
        """
        with get_logger(task="database") as logger:
            try:
                logger.debug('Creating database engine...')
                logger.debug(f'Database URL: {settings.url}')
                self.engine = sa.create_engine(settings.url)
                logger.info('Database engine established successfully.')
                self.Base = declarative_base()
                self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine) # pylint: disable=invalid-name
                self.test_connection()
            except Exception as e:
                err_msg = 'Database engine creation failed'
                logger.exception(err_msg)

    def test_connection(self):
        """
        Test the database connection
        """
        with get_logger(task="database") as logger:
            try:
                logger.debug('Testing database connection...')
                with self.engine.connect() as connection: # pylint: disable=unused-variable
                    logger.info('Database connection tested successfully.')
            except Exception as e:
                err_msg = 'Database connection failed'
                logger.exception(err_msg)
                raise ValueError(err_msg)

    def get_declarative_base(self) -> registry:
        """
        Get the tables registry
        """
        return self.Base

    def get_session(self) -> Session:
        """
        Get a session object
        """
        try:
            return self.SessionLocal()
        except Exception as e:
            err_msg = 'Failed to get session'
            logger.exception(err_msg, task='database', args='')
            raise ValueError(err_msg)

    def create_tables(self):
        """
        Create tables in the database
        """
        with get_logger(task="database") as logger:
            try:
                logger.debug('Creating tables...')
                self.tables_registry.metadata.create_all(self.engine)
                logger.info('Tables created successfully.')
            except Exception as e:
                err_msg = 'Failed to create tables'
                logger.exception(err_msg)
                raise ValueError(err_msg)

    def get_tables(self) -> dict:
        """
        Get all existing tables in the database
        """
        return self.tables_registry.metadata.tables

    def drop_tables(self):
        """
        Drop tables from the database
        """
        with get_logger(task="database") as logger:
            try:
                logger.debug('Dropping tables...')
                self.tables_registry.metadata.drop_all(self.engine)
                logger.info('Tables dropped successfully.')
            except Exception as e:
                err_msg = 'Failed to drop tables'
                logger.error(err_msg)
                raise ValueError(err_msg)

    def reset_tables(self):
        """
        Reset tables in the database
        """
        with get_logger(task="database") as logger:
            logger.debug('Resetting tables...')
            self.drop_tables()
            self.create_tables()
            logger.info('Tables reset successfully.')

    def query_data(self, model) -> list:
        """
        Query data from the database
        """
        with get_logger(task="database") as logger:
            with self.get_session() as session:
                try:
                    logger.debug(f'Querying data from model: {model}')
                    data = session.query(model).all()
                    logger.info(f'Successfully retrieved {len(data)} records.')
                    return data
                except Exception as e:
                    err_msg = 'Failed to query data'
                    logger.exception(err_msg)
                    return []


def get_database_interface() -> DatabaseInterface:
    """
    Get the database interface, specially for dependency injection
    """
    return DatabaseInterface()

from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from .database import get_database_interface, DatabaseInterface
from .logger import LoggerHandler, get_logger, logger
from .schemas import EvaluatorLogin, BulletinQrCode, BulletinForm, EvaluatorCreate
from .handlers import save_bulletin_qr_code


application_router = APIRouter(
    prefix='/application',
    tags=['application', 'admin'],
)

@application_router.post('/evaluator/login', status_code=status.HTTP_200_OK)
def login(
    evaluator: EvaluatorLogin,
    db_connector: DatabaseInterface = Depends(get_database_interface),
):
    """
    Description: Login to the application.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Login requested...')
            logger.debug(f'Phone number: {evaluator.phone_number}')
            logger.debug(f'Section: {evaluator.section}')
            # TODO: Implement login logic
            return {'message': 'Login successful'}
        except Exception as e:
            logger.exception('Login failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@application_router.post('/{section}/bulletin/qrcode', status_code=status.HTTP_201_CREATED)
def create_bulletin_qrcode(
    section: str,
    #token: str,
    bulletin: BulletinQrCode,
    db_connector: DatabaseInterface = Depends(get_database_interface),
):
    """
    Description: Create a bulletin QR code.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Bulletin QR code creation requested...')
            logger.debug(f'Section: {section}')
            #logger.debug(f'Token: {token}')
            logger.debug(f'Bulletin: {bulletin.content}')
            save_bulletin_qr_code(bulletin, section)
        except Exception as e:
            logger.exception('Bulletin QR code creation failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@application_router.post('/{section}/bulletin/form', status_code=status.HTTP_201_CREATED)
def create_bulletin_manually(
    section: str,
    token: str,
    bulletin: BulletinForm,
    db_connector: DatabaseInterface = Depends(get_database_interface),
):
    """
    Description: Create a bulletin manually.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Bulletin creation requested...')
            logger.debug(f'Section: {section}')
            logger.debug(f'Token: {token}')
            logger.debug(f'Bulletin: {bulletin}')
            # TODO: Implement bulletin creation logic
            return {'message': 'Bulletin created successfully'}
        except Exception as e:
            logger.exception('Bulletin creation failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@application_router.get('/evaluator/{evaluator_id}', status_code=status.HTTP_200_OK)
def get_evaluator(
    evaluator_id: int,
    db_connector: DatabaseInterface = Depends(get_database_interface),
):
    """
    Description: Get an evaluator by ID.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Evaluator retrieval requested...')
            logger.debug(f'ID: {evaluator_id}')
            # TODO: Implement evaluator retrieval logic
            return {'message': 'Evaluator retrieved successfully'}
        except Exception as e:
            logger.exception('Evaluator retrieval failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
admin_router = APIRouter(
    prefix='/admin',
    tags=['admin'],
)

@admin_router.post('/evaluator', status_code=status.HTTP_201_CREATED)
def create_evaluator(
    evaluator: EvaluatorCreate,
    db_connector: DatabaseInterface = Depends(get_database_interface),
):
    """
    Description: Create an evaluator.
    """
    with get_logger(task="admin") as logger:
        try:
            logger.debug('Evaluator creation requested...')
            logger.debug(f'Evaluator: {evaluator}')
            # TODO: Implement evaluator creation logic
            return {'message': 'Evaluator created successfully'}
        except Exception as e:
            logger.exception('Evaluator creation failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@admin_router.get('/evaluators', status_code=status.HTTP_200_OK)
def get_evaluators(
    db_connector: DatabaseInterface = Depends(get_database_interface),
):
    """
    Description: Get all evaluators.
    """
    with get_logger(task="admin") as logger:
        try:
            logger.debug('Evaluators retrieval requested...')
            # TODO: Implement evaluators retrieval logic
            return {'message': 'Evaluators retrieved successfully'}
        except Exception as e:
            logger.exception('Evaluators retrieval failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@admin_router.get('/evaluator/{evaluator_id}', status_code=status.HTTP_200_OK)
def get_evaluator(
    evaluator_id: int,
    db_connector: DatabaseInterface = Depends(get_database_interface),
):
    """
    Description: Get an evaluator by ID.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Evaluator retrieval requested...')
            logger.debug(f'ID: {evaluator_id}')
            # TODO: Implement evaluator retrieval logic
            return {'message': 'Evaluator retrieved successfully'}
        except Exception as e:
            logger.exception('Evaluator retrieval failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@admin_router.delete('/evaluator/{evaluator_id}', status_code=status.HTTP_200_OK)
def delete_evaluator(
    evaluator_id: int,
    db_connector: DatabaseInterface = Depends(get_database_interface),
):
    """
    Description: Delete an evaluator by ID.
    """
    with get_logger(task="admin") as logger:
        try:
            logger.debug('Evaluator deletion requested...')
            logger.debug(f'ID: {evaluator_id}')
            # TODO: Implement evaluator deletion logic
            return {'message': 'Evaluator deleted successfully'}
        except Exception as e:
            logger.exception('Evaluator deletion failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@admin_router.post('/candidate', status_code=status.HTTP_201_CREATED)
def create_candidate(
    candidate: EvaluatorCreate,
    db_connector: DatabaseInterface = Depends(get_database_interface),
):
    """
    """
    return {'message': 'Candidate created successfully'}


db_router = APIRouter(
    prefix='/database',
    tags=['database', 'admin'],
    include_in_schema=False
)

@db_router.get('/test-connection',
    summary='Test database connection',
    status_code=status.HTTP_200_OK,
)
def test_connection(
    db_connector: DatabaseInterface = Depends(get_database_interface),
):
    """
    Description: Test the database connection.
    """
    with get_logger(task="database") as logger:
        logger.debug('Database connection test requested...')
        try:
            db_connector.test_connection()
        except Exception as e:
            logger.exception('Database connection test failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@db_router.get(
    '/tables',
    summary='Get all tables in the database',
    description='Get a list of all tables in the database.',
    status_code=status.HTTP_200_OK,
)
def get_tables(
    db_connector: DatabaseInterface = Depends(get_database_interface)
):
    """
    Description: Get a list of all tables in the database.
    """
    tables = db_connector.get_tables()
    return {'tables': tables}

@db_router.get(
    '/tables/create',
    summary='Create tables in the database',
    description='Create tables in the database.',
    status_code=status.HTTP_200_OK,
)
def create_tables(
    db_connector: DatabaseInterface = Depends(get_database_interface)
):
    """
    Description: Create tables in the database.
    """
    db_connector.create_tables()
    return {'message': 'Tables created successfully.'}

@db_router.get(
    '/tables/drop',
    summary='Drop tables in the database',
    description='Drop tables in the database.',
    status_code=status.HTTP_200_OK,
)
def drop_tables(
    db_connector: DatabaseInterface = Depends(get_database_interface)
):
    """
    Description: Drop tables in the database.
    """
    db_connector.drop_tables()
    return {'message': 'Tables dropped successfully.'}

@db_router.get(
    '/tables/reset',
    summary='Reset tables in the database',
    description='Reset tables in the database.',
    status_code=status.HTTP_200_OK,
)
def reset_tables(
    db_connector: DatabaseInterface = Depends(get_database_interface)
):
    """
    Description: Reset tables in the database.
    """
    db_connector.reset_tables()
    return {'message': 'Tables reset successfully.'}

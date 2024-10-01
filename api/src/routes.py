from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from .database import get_database_interface, DatabaseInterface
from .logger import LoggerHandler, get_logger, logger
from .schemas import EvaluatorLogin, BulletinQrCode, BulletinForm, EvaluatorCreate, EvaluatorPublic
from .handlers import save_bulletin_qr_code, validate_evaluator_login


application_router = APIRouter()

@application_router.post('/login', status_code=status.HTTP_200_OK, response_model=EvaluatorPublic)
def login(
    evaluator: EvaluatorLogin,
):
    """
    Description: Login to the application.
    """
    with get_logger(task="login") as logger:
        try:
            logger.debug('Login requested...')
            logger.debug(f'Phone number: {evaluator.phone_number}')
            logger.debug(f'Section: {evaluator.section}')
            return validate_evaluator_login(evaluator)
        except Exception as e:
            logger.exception('Login failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@application_router.post('/bulletin/qrcode', status_code=status.HTTP_201_CREATED)
def create_bulletin_qrcode(
    evaluator: EvaluatorPublic,
    bulletin: BulletinQrCode,
):
    """
    Description: Create a bulletin QR code.
    """
    with get_logger(task="qrcode") as logger:
        try:
            logger.debug('Bulletin QR code creation requested...')
            logger.debug(f'Phone number: {evaluator.phone_number} is creating a bulletin...')
            save_bulletin_qr_code(evaluator, bulletin)
        except Exception as e:
            logger.exception('Bulletin QR code creation failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@application_router.post('/bulletin/form', status_code=status.HTTP_201_CREATED)
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
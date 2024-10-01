from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from .logger import LoggerHandler, get_logger, logger
from .schemas import EvaluatorLogin, BulletinQrCode, EvaluatorPublic, BoletimUrna
from .handlers import save_bulletin_qr_code, get_evaluator, get_bulletin


application_router = APIRouter()

@application_router.post('/evaluator/{phone_number}/login', status_code=status.HTTP_200_OK, response_model=EvaluatorPublic)
def login(
    phone_number: str,
):
    """
    Description: Login to the application.
    """
    with get_logger(task="login") as logger:
        try:
            logger.debug('Login requested...')
            logger.debug(f'Phone number: {phone_number}')
            return get_evaluator(phone_number)
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
    evaluator: EvaluatorPublic,
    bulletin: dict,
):
    """
    Description: Create a bulletin manually.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Bulletin creation requested...')
            logger.debug(f'Phone number: {evaluator.phone_number} is creating a bulletin...')
            logger.debug(f'Bulletin: {bulletin}')
            # TODO: Implement bulletin creation logic
            return {'message': 'Bulletin created successfully'}
        except Exception as e:
            logger.exception('Bulletin creation failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@application_router.get('/bulletin/{phone_number}', status_code=status.HTTP_200_OK, response_model=BoletimUrna)
def get_bulletin_info(
    phone_number:str,
):
    """
    Description: Get the bulletin for the evaluator.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Bulletin retrieval requested...')
            logger.debug(f'Phone number: {phone_number} is retrieving a bulletin...')
            return get_bulletin(phone_number)
        except Exception as e:
            logger.exception('Bulletin retrieval failed')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
from .database import get_database_interface
from .schemas import BulletinQrCode
from .logger import get_logger
from datetime import datetime as dt
from .schemas import EvaluatorLogin, EvaluatorPublic, Header, Content, BoletimUrna
from .models import BoletimUrnaModel
from .utils.bu_parser import BulletinUrnaParser        
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text as Text
import json
import ast


def save_bulletin_qr_code(evaluator: EvaluatorPublic, bulletin: BulletinQrCode):
    """
    Description: Save the QR code for a bulletin.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Bulletin QR code saving requested...')
            parser = BulletinUrnaParser(evaluator.phone_number)
            bulletin = parser.execute(bulletin.content)
            with get_database_interface().get_session() as session:
                bulletin_record = BoletimUrnaModel(
                    evaluator_phone=evaluator.phone_number,
                    type=bulletin.type,
                    finished=bulletin.finished,
                    last_carg=bulletin.last_carg,
                    last_party=bulletin.last_party,
                    open_steps=bulletin.open_steps,
                    header=bulletin.header.json(),
                    content=bulletin.content.json()
                )
                session.add(bulletin_record)
                session.commit()
            logger.info('Bulletin QR code saved successfully.')
        except Exception as e:
            logger.exception('Bulletin QR code saving failed')
            raise e
        
def get_bulletin(phone_number: str):
    """
    Description: Get the bulletin for the evaluator.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Bulletin retrieval requested...')
            with get_database_interface().get_session() as session:
                query = """
                    SELECT type, finished, last_carg, last_party, open_steps, header, content FROM boletim_urna WHERE evaluator_phone = :evaluator_phone
                """ # (!!!!MOCKADOO!!!!)
                result = session.execute(Text(query), {'evaluator_phone': phone_number}).fetchone()
                if not result:
                    logger.warning(f"No bulletin found for phone number: {phone_number}")
                    raise Exception('No bulletin found')
                return BoletimUrna(
                    type=result[0],
                    finished=result[1],
                    last_carg=result[2],
                    last_party=result[3],
                    open_steps=ast.literal_eval(result[4]),
                    header=Header(**json.loads(json.loads(result[5]))),
                    content=Content(**json.loads(json.loads(result[6])))
                )
        except Exception as e:
            logger.exception('Bulletin retrieval failed')
            raise e

def get_evaluator(phone_number):
    """
    Description: Get the evaluator by phone number.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Evaluator retrieval requested...')
            with get_database_interface().get_session() as session:
                query = """
                    SELECT id, phone_number FROM evaluator WHERE phone_number = :phone_number
                """
                result = session.execute(Text(query), {'phone_number': phone_number}).fetchone()
                if not result:
                    logger.warning(f"No evaluator found for phone number: {phone_number}")
                    raise Exception('No evaluator found')
                return EvaluatorPublic(id=result[0], phone_number=result[1])
        except SQLAlchemyError as e:
            logger.exception('Database error occurred during evaluator retrieval')
            raise e  # Re-raise database-specific exceptions for further handling
        except Exception as e:
            logger.exception('An unexpected error occurred during evaluator retrieval')
            raise e  # Re-raise non-database exceptions
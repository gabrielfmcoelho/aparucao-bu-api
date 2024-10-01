from .database import get_database_interface
from .schemas import BulletinQrCode
from .logger import get_logger
from datetime import datetime as dt
from .schemas import EvaluatorLogin, EvaluatorPublic, Header, Content, BoletimUrna
from .models import BoletimUrnaModel
from .utils.bu_parser import BulletinUrnaParser

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
                    open_steps=bulletin.open_steps.json(),
                    header=bulletin.header.json(),
                    content=bulletin.content.json()
                )
                session.add(bulletin_record)
                session.commit()
            logger.info('Bulletin QR code saved successfully.')
        except Exception as e:
            logger.exception('Bulletin QR code saving failed')
            raise e
        
def get_bulletin(evaluator: EvaluatorPublic):
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
                result = session.execute(query, {'evaluator_phone': evaluator.phone_number})
                if not result:
                    raise Exception('No bulletin found')
                return BoletimUrna(
                    type=result[0],
                    finished=result[1],
                    last_carg=result[2],
                    last_party=result[3],
                    open_steps=result[4],
                    header=Header(**result[5]),
                    content=Content(**result[6])
                )
        except Exception as e:
            logger.exception('Bulletin retrieval failed')
            raise e
        
def validate_evaluator_login(evaluator: EvaluatorLogin):
    """
    Description: Validate the evaluator login data.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Validating evaluator login...')
            phone_number = evaluator.phone_number
            with get_database_interface().get_session() as session:
                query = """
                    SELECT id, phone_number FROM evaluator WHERE phone_number = :phone_number 
                """ # (!!!!MOCKADOO!!!!)
                result = session.execute(query, {'phone_number': phone_number})
                if not result:
                    raise Exception('Invalid phone number')
                return EvaluatorPublic(id=result[0], phone_number=result[1])
        except Exception as e:
            logger.exception('Evaluator login validation failed')
            raise e
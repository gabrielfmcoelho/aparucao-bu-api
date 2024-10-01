from .database import get_database_interface
from .models import Bulletin
from .schemas import BulletinQrCode
from .logger import get_logger
from datetime import datetime as dt
from .utils.parsing import parse_qr_code_content

def save_bulletin_qr_code(bulletin: BulletinQrCode, section: str):
    """
    Description: Save the QR code for a bulletin.
    """
    with get_logger(task="application") as logger:
        try:
            logger.debug('Bulletin QR code saving requested...')
            qr_code_content = bulletin.content
            parsed_data = parse_qr_code_content(qr_code_content)
            with get_database_interface().get_session() as session:
                bulletin_record = Bulletin(
                    content=qr_code_content,
                    created_at=dt.utcnow(),
                    updated_at=dt.utcnow(),
                    qr_code_index=int(parsed_data['QRBU'][0]),
                    qr_code_total=int(parsed_data['QRBU'][1]),
                    version=f"{parsed_data['VRQR'][0]}.{parsed_data['VRQR'][1]}",
                    version_key=parsed_data['VRCH'],
                    origin=parsed_data['ORIG'],
                    election_origin=parsed_data['ORLC'],
                    process_number=int(parsed_data['PROC']),
                    election_date=parsed_data['DTPL'],
                    election_number=int(parsed_data['PLEI']),
                    election_turn=int(parsed_data['TURN']),
                    data_phase=parsed_data['FASE'],
                    uf=parsed_data['UNFE'],
                    municipality_number=int(parsed_data['MUNI']),
                    electoral_zone=int(parsed_data['ZONA']),
                    electoral_section=int(parsed_data['SECA']),
                    aggregated_sections=parsed_data['AGRE'],
                    ballot_box_serial=parsed_data['IDUE'],
                    load_id=parsed_data['IDCA'],
                    software_version=parsed_data['VERS'],
                    local_voting_number=int(parsed_data['LOCA']),
                    apt_voters=int(parsed_data['APTO']),
                    present_voters=int(parsed_data['COMP']),
                    absent_voters=int(parsed_data['FALT']),
                    hash_code=parsed_data['HASH'],
                    digital_signature=parsed_data.get('ASSI', None)  # ASSI is optional
                )
                session.add(bulletin_record)
                session.commit()
            logger.info('Bulletin QR code saved successfully.')
        except Exception as e:
            logger.exception('Bulletin QR code saving failed')
            raise e
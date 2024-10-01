from .database import DatabaseInterface, get_database_interface
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy import Enum
from datetime import datetime as dt

Base = get_database_interface().get_declarative_base()

class EvaluatorStatusEnum(str, sa.Enum):
    finished = "finished"
    waiting = "waiting"
    active = "active"
    inactive = "inactive"

# City model
class City(Base):
    __tablename__ = "cities"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(255), nullable=False)
    ibge_code = sa.Column(sa.String(50), nullable=False)
    tse_code = sa.Column(sa.String(50), nullable=False)
    n_candidates = sa.Column(sa.Integer, nullable=False)
    n_zones = sa.Column(sa.Integer, nullable=False)
    n_sections = sa.Column(sa.Integer, nullable=False)

    zones = relationship("Zone", back_populates="city")

# Zone model
class Zone(Base):
    __tablename__ = "zones"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(255), nullable=False)
    n_sections = sa.Column(sa.Integer, nullable=False)
    city_id = sa.Column(sa.Integer, sa.ForeignKey('cities.id'), nullable=False)

    city = relationship("City", back_populates="zones")
    sections = relationship("Section", back_populates="zone")

# Section model
class Section(Base):
    __tablename__ = "sections"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(255), nullable=False)
    zone_id = sa.Column(sa.Integer, sa.ForeignKey('zones.id'), nullable=False)

    zone = relationship("Zone", back_populates="sections")
    bulletins = relationship("Bulletin", back_populates="section")

# Evaluator model
class Evaluator(Base):
    __tablename__ = "evaluators"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(255), nullable=False)
    phone_number = sa.Column(sa.String(20), nullable=False)
    status = sa.Column(sa.Enum, nullable=False, default=EvaluatorStatusEnum.waiting)
    city_id = sa.Column(sa.Integer, sa.ForeignKey('cities.id'), nullable=False)
    zone_id = sa.Column(sa.Integer, sa.ForeignKey('zones.id'), nullable=False)
    section_id = sa.Column(sa.Integer, sa.ForeignKey('sections.id'), nullable=False)

    city = relationship("City")
    zone = relationship("Zone")
    section = relationship("Section")

# Bulletin model
class Bulletin(Base):
    __tablename__ = "bulletins"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    content = sa.Column(sa.Text, nullable=False)  # Raw QR code content
    created_at = sa.Column(sa.DateTime, default=dt.utcnow, nullable=False)
    updated_at = sa.Column(sa.DateTime, default=dt.utcnow, onupdate=dt.utcnow, nullable=False)
    
    # Additional fields from the QR code bulletin data
    qr_code_index = sa.Column(sa.Integer, nullable=False)  # n in QRBU:n:x
    qr_code_total = sa.Column(sa.Integer, nullable=False)  # x in QRBU:n:x
    version = sa.Column(sa.String(10), nullable=False)  # VRQR:n.y
    version_key = sa.Column(sa.String(50), nullable=False)  # VRCH:nnnn
    origin = sa.Column(sa.String(10), nullable=False)  # ORIG:xxxx
    election_origin = sa.Column(sa.String(10), nullable=False)  # ORLC:xxx
    process_number = sa.Column(sa.Integer, nullable=False)  # PROC:nnnnn
    election_date = sa.Column(sa.Date, nullable=False)  # DTPL:aaaammdd
    election_number = sa.Column(sa.Integer, nullable=False)  # PLEI:nnnnn
    election_turn = sa.Column(sa.Integer, nullable=False)  # TURN:n
    data_phase = sa.Column(sa.String(1), nullable=False)  # FASE:x
    uf = sa.Column(sa.String(2), nullable=False)  # UNFE:xx
    municipality_number = sa.Column(sa.Integer, nullable=False)  # MUNI:nnnnn
    electoral_zone = sa.Column(sa.Integer, nullable=False)  # ZONA:nnnn
    electoral_section = sa.Column(sa.Integer, nullable=False)  # SECA:nnnn
    aggregated_sections = sa.Column(sa.String(255))  # AGRE:nnnn.nnnn
    ballot_box_serial = sa.Column(sa.String(255), nullable=False)  # IDUE:nnnn...
    load_id = sa.Column(sa.String(24), nullable=False)  # IDCA:nnnn...
    software_version = sa.Column(sa.String(255), nullable=False)  # VERS:xxxx...
    junta_number = sa.Column(sa.Integer)  # JUNT:nnnn (optional)
    turma_number = sa.Column(sa.Integer)  # TURM:nnnn (optional)
    emission_date = sa.Column(sa.Date, nullable=False)  # DTEM:aaaammdd
    emission_time = sa.Column(sa.Time, nullable=False)  # HREM:hhmmss
    local_voting_number = sa.Column(sa.Integer)  # LOCA:nnnn
    apt_voters = sa.Column(sa.Integer)  # APTO:nnnn
    present_voters = sa.Column(sa.Integer)  # COMP:nnnn
    absent_voters = sa.Column(sa.Integer)  # FALT:nnnn
    hash_code = sa.Column(sa.String(512), nullable=False)  # HASH:xxxxxx...
    digital_signature = sa.Column(sa.String(512), nullable=True)  # ASSI:xxxxxx...

    section_id = sa.Column(sa.Integer, sa.ForeignKey('sections.id'), nullable=False)
    section = relationship("Section", back_populates="bulletins")

    def __repr__(self):
        return f"<Bulletin id={self.id}, election_number={self.election_number}, election_turn={self.election_turn}>"
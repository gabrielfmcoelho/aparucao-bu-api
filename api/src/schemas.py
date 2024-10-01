from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, constr, conint, Field
from typing_extensions import Annotated
from datetime import date, datetime
import re

class Bulletin(BaseModel):
    id: int
    section: str
    content: str
    created_at: str
    updated_at: str

class EvaluatorStatus(str, Enum):
    finished = 'finished'
    waiting = 'waiting'
    active = 'active'
    inactive = 'inactive'

class EvaluatorLogin(BaseModel):
    section: str
    phone_number: str

class EvaluatorCreate(EvaluatorLogin):
    name: str = ''
    city: str = ''
    status: EvaluatorStatus = EvaluatorStatus.active
    bulletins: list[Bulletin] = []

class EvaluatorPublic(EvaluatorCreate):
    id: int

class BulletinQrCode(BaseModel):
    content: str

class BulletinForm(BaseModel):
    section: str

# Define the Pydantic models

from pydantic import BaseModel
from typing import List, Dict, Optional

class VotingSummary(BaseModel):
    APTA: int = None
    APTS: int = None
    APTT: int = None
    CSEC: Optional[int] = None
    NOMI: int = None
    LEGC: Optional[int] = None  # Only for proportional
    BRAN: int = None
    NULO: int = None
    TOTC: int = None

class Candidate(BaseModel):
    code: str = None
    votes: int = None
 
class Party(BaseModel):
    PART: int = None
    LEGP: int = None
    TOTP: int = None
    candidates: Dict[str, Candidate] = {}

class Position(BaseModel):
    CARG: int = None
    TIPO: int = None
    VERC: int = None
    summary: VotingSummary = VotingSummary()
    party: List[Party] = []

class VotingData(BaseModel):
    IDEL: int = None
    position: List[Position] = []

class SecurityData(BaseModel):
    HASH: str = None
    ASSI: str = None

class Metadata(BaseModel):
    ORIG: str = None
    ORLC: str = None
    PROC: int = None
    DTPL: str = None
    PLEI: int = None
    TURN: int = None
    FASE: str = None
    UNFE: str = None
    MUNI: int = None
    ZONA: int = None
    SECA: int = None
    AGRE: List[float] = []
    IDUE: int = None
    IDCA: int = None
    HIQT: int = None
    HICA: str = None
    VERS: str = None

class Details(BaseModel):
    LOCA: int = None
    APTO: int = None
    APTS: int = None
    APTT: int = None
    COMP: int = None
    FALT: int = None
    HBBM: int = None 
    HBBG: int = None
    HBSB: int = None
    DTAB: str = None
    HRAB: str = None
    DTFC: str = None
    HRFC: str = None

class Header(BaseModel):
    QRBU: list[int] = []
    VRQR: str = None
    VRCH: str = None

class Content(BaseModel):
    metadata: Metadata = Metadata()
    details: Details = Details()
    voting: VotingData = VotingData()
    security: SecurityData = SecurityData()

class BoletimUrna(BaseModel):
    header: Header
    content: Content
    
class BoletimUrnaContainer(BaseModel):
    bu: List[BoletimUrna]
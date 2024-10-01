from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, constr, conint, Field
from typing_extensions import Annotated
from datetime import date, datetime
from dataclasses import dataclass
import re

class EvaluatorLogin(BaseModel):
    phone_number: str    

class EvaluatorPublic(EvaluatorLogin):
    id: int

class BulletinQrCode(BaseModel):    
    content: str

class VotingSummary(BaseModel):
    APTA: Optional[int] = None
    APTS: Optional[int] = None
    APTT: Optional[int] = None
    CSEC: Optional[int] = None
    NOMI: Optional[int] = None
    LEGC: Optional[int] = None  # Only for proportional
    BRAN: Optional[int] = None
    NULO: Optional[int] = None
    TOTC: Optional[int] = None

class Candidate(BaseModel):
    code: Optional[str] = None
    votes: Optional[int] = None
 
class Party(BaseModel):
    PART: Optional[int] = None
    LEGP: Optional[int] = None
    TOTP: Optional[int] = None
    candidates: Dict[str, Candidate] = {}

class Position(BaseModel):
    CARG: Optional[int] = None
    TIPO: Optional[int] = None
    VERC: Optional[int] = None
    summary: VotingSummary = VotingSummary()
    party: List[Party] = []

class VotingData(BaseModel):
    IDEL: Optional[int]= None
    position: List[Position] = []

class SecurityData(BaseModel):
    HASH: Optional[str] = None
    ASSI: Optional[str] = None

class Metadata(BaseModel):
    ORIG: Optional[str] = None
    ORLC: Optional[str] = None
    PROC: Optional[int] = None
    DTPL: Optional[str] = None
    PLEI: Optional[int] = None
    TURN: Optional[int] = None
    FASE: Optional[str] = None
    UNFE: Optional[str] = None
    MUNI: Optional[int] = None
    ZONA: Optional[int] = None
    SECA: Optional[int] = None
    AGRE: List[float] = []
    IDUE: Optional[int] = None
    IDCA: Optional[int] = None
    HIQT: Optional[int] = None
    HICA: Optional[list[str]] = None
    VERS: Optional[str] = None

class Details(BaseModel):
    LOCA: Optional[int] = None
    APTO: Optional[int] = None
    APTS: Optional[int] = None
    APTT: Optional[int] = None
    COMP: Optional[int] = None
    FALT: Optional[int] = None
    HBBM: Optional[int] = None 
    HBBG: Optional[int] = None
    HBSB: Optional[int] = None
    DTAB: Optional[str] = None
    HRAB: Optional[str] = None
    DTFC: Optional[str] = None
    HRFC: Optional[str] = None

class Header(BaseModel):
    QRBU: list[int] = []
    VRQR: Optional[str] = None
    VRCH: Optional[str] = None

class Content(BaseModel):
    metadata: Metadata = Metadata()
    details: Details = Details()
    voting: VotingData = VotingData()
    security: SecurityData = SecurityData()

class BoletimUrna(BaseModel):
    type: str
    finished: bool
    last_carg: int
    last_party: int|None
    open_steps: List[str]|None
    header: Header
    content: Content

class BoletimUrnaForm(BaseModel):
    pass

class ProcessingStep(Enum):
        WAITING: str = "waiting"
        OPEN: str = "open"
        FINISHED: str = "finished"

@dataclass
class ProcessingStatus:
    header: ProcessingStep = ProcessingStep.OPEN
    context_setup: ProcessingStep = ProcessingStep.WAITING
    content: ProcessingStep = ProcessingStep.WAITING
    metadata: ProcessingStep = ProcessingStep.WAITING
    details: ProcessingStep = ProcessingStep.WAITING
    voting: ProcessingStep = ProcessingStep.WAITING
    position: ProcessingStep = ProcessingStep.WAITING
    party: ProcessingStep = ProcessingStep.WAITING
    candidate: ProcessingStep = ProcessingStep.WAITING
    summary: ProcessingStep = ProcessingStep.WAITING
    security: ProcessingStep = ProcessingStep.OPEN
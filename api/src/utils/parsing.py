import re
from typing import Dict, Union, List
from ..schemas import *
from datetime import datetime
from pydantic import BaseModel

# Suponha que essas classes já estejam definidas no código

def parse_boletim_urna_string(bu_string: str) -> BoletimUrna:
    # Dividimos a string por espaços para obter cada chave-valor separadamente
    parts = re.split(r'\s+', bu_string)
    
    # Criamos dicionários para armazenar os valores
    header = Header()
    content = Content()
    current_position = None
    current_party = None
    current_candidates = {}

    for part in parts:
        key_value = part.split(":")
        # header
        if key_value[0] in ["QRBU", "VRQR", "VRCH"]:
            if key_value[0] == "QRBU":
                header.QRBU = [int(k) for k in key_value[1:]]
            elif key_value[0] == "VRQR":
                header.VRQR = key_value[1]
            elif key_value[0] == "VRCH":
                header.VRCH = key_value[1]
        # content
        else:
            # metadata
            if key_value[0] in ["ORIG", "ORLC", "FASE", "UNFE", "HICA", "VERS"]:
                if key_value[0] == "ORIG":
                    content.metadata.ORIG = key_value[1]
                elif key_value[0] == "ORLC":
                    content.metadata.ORLC = key_value[1]
                elif key_value[0] == "FASE":
                    content.metadata.FASE = key_value[1]
                elif key_value[0] == "UNFE":
                    content.metadata.UNFE = key_value[1]
                elif key_value[0] == "HICA":
                    content.metadata.HICA = key_value[1]
                elif key_value[0] == "VERS":
                    content.metadata.VERS = key_value[1]
            elif key_value[0] in ["PROC", "PLEI", "TURN", "MUNI", "ZONA", "SECA", "IDUE", "IDCA", "HIQT"]:
                if key_value[0] == "PROC":
                    content.metadata.PROC = int(key_value[1])
                elif key_value[0] == "PLEI":
                    content.metadata.PLEI = int(key_value[1])
                elif key_value[0] == "TURN":
                    content.metadata.TURN = int(key_value[1])
                elif key_value[0] == "MUNI":
                    content.metadata.MUNI = int(key_value[1])
                elif key_value[0] == "ZONA":
                    content.metadata.ZONA = int(key_value[1])
                elif key_value[0] == "SECA":
                    content.metadata.SECA = int(key_value[1])
                elif key_value[0] == "IDUE":
                    content.metadata.IDUE = int(key_value[1])
                elif key_value[0] == "IDCA":
                    content.metadata.IDCA = int(key_value[1])
                elif key_value[0] == "HIQT":
                    content.metadata.HIQT = int(key_value[1])
            elif key_value[0] == "DTPL":
                content.metadata.DTPL = datetime.strptime(key_value[1], '%Y%m%d').strftime('%Y-%m-%d')
            elif key_value[0] == "AGRE":
                content.metadata.AGRE = [float(key_value[1])]
            # details
            elif key_value[0] in ["LOCA", "APTO", "APTS", "APTT", "COMP", "FALT", "HBBM", "HBBG", "HBSB"]:
                if key_value[0] == "LOCA":
                    content.details.LOCA = int(key_value[1])
                elif key_value[0] == "APTO":
                    content.details.APTO = int(key_value[1])
                elif key_value[0] == "APTS":
                    content.details.APTS = int(key_value[1])
                elif key_value[0] == "APTT":
                    content.details.APTT = int(key_value[1])
                elif key_value[0] == "COMP":
                    content.details.COMP = int(key_value[1])
                elif key_value[0] == "FALT":
                    content.details.FALT = int(key_value[1])
                elif key_value[0] == "HBBM":
                    content.details.HBBM = int(key_value[1])
                elif key_value[0] == "HBBG":
                    content.details.HBBG = int(key_value[1])
                elif key_value[0] == "HBSB":
                    content.details.HBSB = int(key_value[1])
            elif key_value[0] == "DTAB":
                content.details.DTAB = datetime.strptime(key_value[1], '%Y%m%d').strftime('%Y-%m-%d')
            elif key_value[0] == "HRAB":
                content.details.HRAB = key_value[1]
            elif key_value[0] == "DTFC":
                content.details.DTFC = datetime.strptime(key_value[1], '%Y%m%d').strftime('%Y-%m-%d')
            elif key_value[0] == "HRFC":
                content.details.HRFC = key_value[1]
            # voting
            elif key_value[0] == "IDEL":
                content.voting.IDEL = int(key_value[1])
            # position
            elif key_value[0] == "CARG":
                if current_position:
                    content.voting.position.append(current_position)
                current_position = Position(CARG=int(key_value[1]))
            elif key_value[0] == "TIPO":
                current_position.TIPO = int(key_value[1])
            elif key_value[0] == "VERC":
                current_position.VERC = int(key_value[1])
            # party
            elif key_value[0] == "PART":
                if current_party:
                    current_party.candidates = current_candidates
                    current_position.party.append(current_party)
                current_candidates = {}
                current_party = Party(PART=int(key_value[1]))
            elif key_value[0] == "LEGP":
                current_party.LEGP = int(key_value[1])
            elif key_value[0] == "TOTP":
                current_party.TOTP = int(key_value[1])
            elif len(key_value[0]) == 5 and key_value[0].isdigit():
                current_candidates[key_value[0]] = Candidate(code=key_value[0], votes=int(key_value[1]))
            elif key_value[0] == "APTA":
                current_position.summary = VotingSummary(
                    APTA=int(key_value[1]),
                    APTS=int(parts[parts.index(part) + 1].split(":")[1]),
                    APTT=int(parts[parts.index(part) + 2].split(":")[1]),
                    NOMI=int(parts[parts.index(part) + 3].split(":")[1]),
                    BRAN=int(parts[parts.index(part) + 4].split(":")[1]),
                    NULO=int(parts[parts.index(part) + 5].split(":")[1]),
                    TOTC=int(parts[parts.index(part) + 6].split(":")[1])
                )
                if 'LEGC' in key_value:
                    current_position.summary.LEGC = int(parts[parts.index(part) + 7].split(":")[1])
            # security
            elif key_value[0] == "HASH":
                content.security.HASH = key_value[1]
            elif key_value[0] == "ASSI":
                content.security.ASSI = key_value[1]

    # Finalmente, inserimos o último partido e a última posição
    if current_party:
        current_party.candidates = current_candidates
        current_position.party.append(current_party)
    if current_position:
        content.voting.position.append(current_position)
    
    return BoletimUrna(header=header, content=content)
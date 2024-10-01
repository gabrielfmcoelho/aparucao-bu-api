from ..schemas import *
import json
from ..database import DatabaseInterface, get_database_interface

class BulletinUrnaParser:
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.parsing_processing_status = ProcessingStatus()
        self.header = Header()
        self.content = Content()
        self.current_position = None
        self.current_party = None
        self.current_candidates = {}
        self.parsed_bulletin = None
        self.empty_party = False
        self.counters = {
            "header": [3, 0],
            "metadata": [17, 0],
            "details": [13, 0],
            "voting": [2, 0],
            "position": [4, 0],
            "party": [0, 0],
            "candidate": [0, 0],
            "summary": [0, 0],
            "security": [0, 0]
        }
        self.counter = 0

    def _get_last_bu(self):
        # Lazy load from mock DB or real DB
        with get_database_interface().get_session() as session:
            query = """
                SELECT type, finished, last_carg, last_party, open_steps, header, content FROM boletim_urna WHERE evaluator_phone = :evaluator_phone
            """
            result = session.execute(query, {'evaluator_phone': self.phone_number})
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
        return bulletin

    def _update_status(self, step:list = None, next_step:list = None):
        if step:
            for s in step:
                self.parsing_processing_status.__setattr__(s, ProcessingStep.FINISHED)
                print(f"Finished processing step: {s}")
        if next_step:
            for s in next_step:
                self.parsing_processing_status.__setattr__(s, ProcessingStep.OPEN)
                print(f"Opened processing step: {s}")

    def _update_counter(self, step):
        self.counters[step][1] += 1
        #if self.counters[step][1] == self.counters[step][0]:
            #self._update_status([step], [self.counters[step][0]])

    def _parse_field(self, key_value, field_mapping, steps_status: list, obj_nickname=str):
        key = key_value[0]
        value = key_value[1:] if len(key_value) > 2 else key_value[1]
        if key in field_mapping and self._validate_open_steps(steps_status):
            attr, is_int, fmt, step, next_step = field_mapping[key]
            value = int(value) if is_int else value
            if fmt:  # If there's formatting to apply (e.g., date formatting)
                value = fmt(value)
    
            obj_nicknames = {
                "header": self.header,
                "content": self.content,
                "position": self.current_position,
                "party": self.current_party,
            }
            obj = obj_nicknames[obj_nickname]
            attr_parts = attr.split(".")
            for part in attr_parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, attr_parts[-1], value)

            self._update_status(step, next_step)
            return True
        return False
    
    def _code_size(self):
        return "large" if self.header.QRBU[1] > 1 else "small"
    
    def _is_first_code(self):
        return self.header.QRBU[0] == 1
    
    def _is_finished(self):
        return (self.header.QRBU[0] == self.header.QRBU[1]) and self.content.security.ASSI is not None
    
    def _check_continuity(self, last_QRBU, current_QRBU):
        if not last_QRBU[0] + 1 == current_QRBU[0]:
            raise ValueError(f"Boletim não está em sequencia, esperado {last_QRBU[0] + 1}, recebeu {current_QRBU[0]}")
        
    def _set_open_steps_in_context(self, open_steps:list):
        for step in open_steps:
            self.parsing_processing_status.__setattr__(step, ProcessingStep.OPEN)

    def _get_open_steps(self):
        return [k for k, v in self.parsing_processing_status.__dict__.items() if v == ProcessingStep.OPEN]
    
    def _validate_open_steps(self, steps):
        open_steps = self._get_open_steps()
        n_ok = 0
        for step in steps:
            if step in open_steps:
                n_ok += 1
        if n_ok == len(steps):
            return True
        return False
    
    # Parsing Header Fields
    def _parse_header(self, key_value):
        field_mapping = {
            "QRBU": ("QRBU", False, lambda v: [int(k) for k in v], None, None),
            "VRQR": ("VRQR", False, None, None, None),
            "VRCH": ("VRCH", False, None, ["header"], ["context_setup"]),
        }
        return self._parse_field(key_value, field_mapping, ["header", "security"], "header")
    
    def _set_context(self):
        if self.parsing_processing_status.context_setup == ProcessingStep.OPEN:
            if self._code_size() == "large" and not self._is_first_code():
                print("Attempting to continue")
                last_bulletin = self._get_last_bu()
                last_carg = last_bulletin.last_carg
                last_party = last_bulletin.last_party
                open_steps = last_bulletin.open_steps
                print(f"Retrieved last bulletin with last_carg: {last_carg} and last_party: {last_party} and QRBU: {last_bulletin.header.QRBU} to continue parsing")
                self._check_continuity(last_bulletin.header.QRBU, self.header.QRBU)
                last_bulletin.header.QRBU[0] = self.header.QRBU[0] # Update last bulletin QRBU to current QRBU
                self.header = last_bulletin.header
                self.content = last_bulletin.content
                self._update_status(next_step=open_steps)
                # current position is the object that contains CARG == last_carg
                for p in self.content.voting.position:
                    if p.CARG == last_carg:
                        self.current_position = p
                # current party if it is not None is the last_party or where PART == last_party
                if last_party:
                    for p in self.current_position.party:
                        if p.PART == last_party:
                            self.current_party = p
                    if not self.current_party:
                        self.current_party = self.current_position.party[-1]
                    self.current_candidates = self.current_party.candidates
                self._update_status(step=["context_setup"])
            else:
                print("small or first large")
                self._update_status(step=["context_setup"], next_step=["content", "metadata"])
        return False

    # Parsing Metadata Fields
    def _parse_metadata(self, key_value):
        field_mapping = {
            "ORIG": ("metadata.ORIG", False, None, None, None),
            "ORLC": ("metadata.ORLC", False, None, None, None),
            "PROC": ("metadata.PROC", True, None, None, None),
            "DTPL": ("metadata.DTPL", False, lambda v: datetime.strptime(v, '%Y%m%d').strftime('%Y-%m-%d'), None, None),
            "PLEI": ("metadata.PLEI", True, None, None, None),
            "TURN": ("metadata.TURN", True, None, None, None),
            "FASE": ("metadata.FASE", False, None, None, None),
            "UNFE": ("metadata.UNFE", False, None, None, None),
            "MUNI": ("metadata.MUNI", True, None, None, None),
            "ZONA": ("metadata.ZONA", True, None, None, None),
            "SECA": ("metadata.SECA", True, None, None, None),
            "AGRE": ("metadata.AGRE", False, lambda v: [int(k) for k in v.split(".")], None, None),
            "IDUE": ("metadata.IDUE", True, None, None, None),
            "IDCA": ("metadata.IDCA", True, None, None, None),
            "HIQT": ("metadata.HIQT", True, None, None, None),
            "HICA": ("metadata.HICA", False, None, None, None),
            "VERS": ("metadata.VERS", False, None, ["metadata"], ["details"]),
        }
        return self._parse_field(key_value, field_mapping, ["content", "metadata", "security"], "content")

    # Parsing Details Fields
    def _parse_details(self, key_value):
        field_mapping = {
            "LOCA": ("details.LOCA", True, None, None, None),
            "APTO": ("details.APTO", True, None, None, None),
            "APTS": ("details.APTS", True, None, None, None),
            "APTT": ("details.APTT", True, None, None, None),
            "COMP": ("details.COMP", True, None, None, None),
            "FALT": ("details.FALT", True, None, None, None),
            "HBBM": ("details.HBBM", True, None, None, None),
            "HBBG": ("details.HBBG", True, None, None, None),
            "HBSB": ("details.HBSB", True, None, None, None),
            "DTAB": ("details.DTAB", False, lambda v: datetime.strptime(v, '%Y%m%d').strftime('%Y-%m-%d'), None, None),
            "HRAB": ("details.HRAB", False, lambda v: f"{v[:2]}:{v[2:4]}:{v[4:]}", None, None),
            "DTFC": ("details.DTFC", False, lambda v: datetime.strptime(v, '%Y%m%d').strftime('%Y-%m-%d'), None, None),
            "HRFC": ("details.HRFC", False, lambda v: f"{v[:2]}:{v[2:4]}:{v[4:]}", ["details"], ["voting"]),
        }
        return self._parse_field(key_value, field_mapping, ["content", "details", "security"], "content")

    # Parsing Voting Fields
    def _parse_voting(self, key_value):
        field_mapping = {
            "IDEL": ("voting.IDEL", True, None, None, ["position"]),
        }
        return self._parse_field(key_value, field_mapping, ["content", "voting", "security"], "content")

    # Parsing Position Fields
    def _parse_position(self, key_value):
        field_mapping = {
            "CARG": ("CARG", True, None, None, None),
            "TIPO": ("TIPO", True, None, None, None),
            "VERC": ("VERC", True, None, None, ["party"]),
        }
        if key_value[0] == "CARG":
                self.empty_party = True if int(key_value[1]) == 11 else False
                print(f"Empty party: {self.empty_party}")
                if (self.current_position and self.current_position.CARG != int(key_value[1])):
                    print("ATTENTION: New CARG found")
                    # check if the current_position CARG exits in the content.voting.position if not append if yes delete and append
                    if self.current_party:
                        self.current_position.party.append(self.current_party)
                    if not any(p.CARG == self.current_position.CARG for p in self.content.voting.position):
                        self.content.voting.position.append(self.current_position)
                    else:
                        self.content.voting.position = [p for p in self.content.voting.position if p.CARG != self.current_position.CARG]
                        self.content.voting.position.append(self.current_position)
                self.current_position = Position()
                self.current_party = None
                self.current_candidates = {}
        return self._parse_field(key_value, field_mapping, ["content", "voting", "position", "security"], "position")

    # Parsing Party Fields
    def _parse_party(self, key_value):
        field_mapping = {
            "PART": ("PART", True, None, None, ["candidate"]),
        }
        print((self.empty_party and self.parsing_processing_status.candidate == ProcessingStep.WAITING))
        if key_value[0] == "PART" or (self.empty_party and self.parsing_processing_status.candidate != ProcessingStep.OPEN and self.parsing_processing_status.summary != ProcessingStep.OPEN and key_value[0] != "HASH"):
            print("ATTENTION: New PART found")
            if self.empty_party and self.parsing_processing_status.candidate != ProcessingStep.OPEN:
                self._update_status(next_step=["candidate"])
            if self.current_party:
                current_party_first_candidate = list(self.current_party.candidates.keys())[0]
                party_to_delete = None
                for party in self.current_position.party:
                    first_candidate = list(party.candidates.keys())[0]
                    print(f"Current party first candidate: {current_party_first_candidate}, First candidate: {first_candidate}")
                    if current_party_first_candidate == first_candidate:
                        print("ATTENTION: same party found")
                        party_to_delete = party
                if party_to_delete:
                    print("Deleting party")
                    self.current_position.party = [p for p in self.current_position.party if p != party_to_delete]
                self.current_position.party.append(self.current_party)
            print("Creating party")
            self.current_party = Party()
            self.current_candidates = {}
        return self._parse_field(key_value, field_mapping, ["content", "voting", "position", "party", "security"], "party")

    def _is_candidate(self, key_value):
        try:
            int(key_value[0])
            return True
        except:
            return False

    def _verify_next_candidate_exists(self):
        return self.next_part and self._is_candidate(self.next_part.split(":"))

    # Parsing Candidate Fields
    def _parse_candidate(self, key_value):
        if self._is_candidate(key_value) and self._validate_open_steps(["content", "voting", "position", "party", "candidate", "security"]):
            self.current_candidates[key_value[0]] = Candidate(code=key_value[0], votes=int(key_value[1]))
            if not self._verify_next_candidate_exists():
                self._update_status(step=["candidate"], next_step=["summary"])
                self.current_party.candidates = self.current_candidates
                self.current_candidates = {}
            return True
        return False
    
    # Parsing POST Party Fields
    def _parse_post_party(self, key_value):
        field_mapping = {
            "LEGP": ("LEGP", True, None, None, None),
            "TOTP": ("TOTP", True, None, None, None),
        }
        return self._parse_field(key_value, field_mapping, ["content", "voting", "position", "party", "summary", "security"], "party")

    # Parsing Summary Fields
    def _parse_summary(self, key_value):
        field_mapping = {
            "APTA": ("summary.APTA", True, None, None, None),
            "APTS": ("summary.APTS", True, None, None, None),
            "APTT": ("summary.APTT", True, None, None, None),
            "NOMI": ("summary.NOMI", True, None, None, None),
            "BRAN": ("summary.BRAN", True, None, None, None),
            "NULO": ("summary.NULO", True, None, None, None),
            "LEGC": ("summary.LEGC", True, None, None, None),
            "TOTC": ("summary.TOTC", True, None, ["summary"], None),
        }
        return self._parse_field(key_value, field_mapping, ["content", "voting", "position", "party", "summary", "security"], "position")

    # Parsing Security Fields
    def _parse_security(self, key_value):
        field_mapping = {
            "HASH": ("security.HASH", False, None, None, None),
            "ASSI": ("security.ASSI", False, None, ["content", "position", "party", "security"], None),
        }
        if key_value[0] == "HASH":
            if self.current_party:
                self.current_position.party.append(self.current_party)
            if self.current_position:
                if any(p.CARG == self.current_position.CARG for p in self.content.voting.position):
                    self.content.voting.position = [p for p in self.content.voting.position if p.CARG != self.current_position.CARG]
                self.content.voting.position.append(self.current_position)
            if self.next_part == None: 
                self._update_status(next_step=["candidate"])
        return self._parse_field(key_value, field_mapping, ["content", "security"], "content")

    # Main execute function
    def execute(self, bu_string: str) -> BoletimUrna:
        parts = re.split(r'\s+', bu_string)
        print(f"Initiating parsing of bulletin")
        print(f"Opened processing step: header")
        print(f"Processing steps with OPEN status on start: {self._get_open_steps()}")
        for part in parts:
            print(f"Counter: {self.counters}")
            key_value = part.split(":")
            print(f"Processing key_value: {key_value}")

            self.next_part = parts[self.counter + 1] if self.counter + 1 < len(parts) else None
            self.counter += 1

            # Parse in order and skip if handled
            if self._parse_header(key_value):
                print(f"executed header")
                self._update_counter("header")
                continue

            elif self._set_context():
                pass

            elif self._parse_metadata(key_value):
                print(f"executed metadata")
                self._update_counter("metadata")
                continue

            elif self._parse_details(key_value):
                print(f"executed details")
                self._update_counter("details")
                continue

            elif self._parse_voting(key_value):
                print(f"executed voting")
                self._update_counter("voting")
                continue

            elif self._parse_position(key_value):
                print(f"executed position")
                self._update_counter("position")
                continue

            elif self._parse_party(key_value):
                print(f"executed party")
                self._update_counter("party")
                continue

            elif self._parse_candidate(key_value):
                print(f"executed candidate")
                self._update_counter("candidate")
                continue

            elif self._parse_post_party(key_value):
                self._update_counter("party")
                continue

            elif self._parse_summary(key_value):
                self._update_counter("summary")
                continue

            elif self._parse_security(key_value):
                self._update_counter("security")
                continue
        
        print("FINISHED PARSING")
        print(f"Processing steps with OPEN status on start: {self._get_open_steps()}")
        
        # At the end, assemble the bulletin
        self.parsed_bulletin = BoletimUrna(
            type=self._code_size(),
            finished=self._is_finished(),
            last_carg=self.current_position.CARG,
            last_party=self.current_party.PART if self.current_party else None,
            open_steps=self._get_open_steps(),
            header=self.header,
            content=self.content
        )
        return self.parsed_bulletin

    def export_json(self, name: str):
        with open(name, 'w') as f:
            json.dump(self.parsed_bulletin.dict(), f, indent=4)
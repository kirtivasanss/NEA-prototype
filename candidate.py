from dataclasses import dataclass


@dataclass
class Candidate:
    name: str
    email: str
    phone: str
    location: str
    education: str
    experience: str
    skills: list
    currentRole: str
    company: str
    candidate_id: int = None

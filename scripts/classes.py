from dataclasses import dataclass


@dataclass
class EducationalProgram:
    university: str
    name: str
    sub_name: str
    budget_places: int
    contract: int


@dataclass
class AbiturSimplified:
    unique_code: str | int  # snils
    score: int  # exam results + personal achievements
    wet: bool  # without entrance tests
    competitive: str
    orig_cert: bool  # original certificate
    priority: int
    ep_name: str


@dataclass
class MIPTCompetitiveDev:
    name: str
    sub_name: str
    competitive: str
    url: str


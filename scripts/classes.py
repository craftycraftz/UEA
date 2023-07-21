import enum
from dataclasses import dataclass


class Competitive(enum.Enum):
    BUDGET = "budget"
    SPECIAL_QUOTA = "special_quota"
    SEPARATE_QUOTA = "separate_quota"
    TARGET_QUOTA = "target_quota"
    CONTRACT = "contract"


@dataclass
class EducationalProgram:
    university_name: str
    code: str
    name: str
    budget_places: int
    special_quota_places: int
    separate_quota_places: int
    target_quota_places: int
    contract_places: int
    price: int

    def to_database_format(self) -> tuple:
        """"""
        return tuple(self.__dict__.values())


@dataclass
class Abitur:
    unique_code: str | int  # snils
    place: int
    score: int  # exam results + personal achievements
    wet: bool  # without entrance tests
    competitive: Competitive
    orig_cert: bool  # original certificate
    priority: int
    ep_id: int

    def to_database_format(self) -> tuple:
        """"""
        orig = int(self.orig_cert)
        contr = 1 if self.competitive == Competitive.CONTRACT else 0
        benefits = "1" if self.wet else "0"
        benefits += "1" if self.competitive == Competitive.SPECIAL_QUOTA else "0"
        benefits += "1" if self.competitive == Competitive.SEPARATE_QUOTA else "0"
        benefits += "1" if self.competitive == Competitive.TARGET_QUOTA else "0"

        return self.unique_code, orig, self.place, self.score, contr, benefits, self.priority, self.ep_id


@dataclass
class MIPTCompetitiveGroupDev:
    code: str
    name: str
    ep_id: int
    competitive: Competitive
    url: str

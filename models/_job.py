from dataclasses import dataclass


@dataclass
class Job:
    category: str
    company: str
    date_from: str
    date_to: str
    name: str
    place: str
    url: str

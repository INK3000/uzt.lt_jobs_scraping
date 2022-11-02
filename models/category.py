from dataclasses import dataclass, field


@dataclass
class Category:
    name: str
    event_target: str
    jobs_list: list = field(default_factory=list)
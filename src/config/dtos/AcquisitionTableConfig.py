from dataclasses import dataclass


@dataclass
class AcquisitionTableConfig:
    name: str
    attribute: str
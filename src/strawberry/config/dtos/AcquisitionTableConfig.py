from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json

@dataclass
class ColumnConfig:
    """
    Represents the schema and validation rules for a single column.
    """
    name: str
    type: str
    format: Optional[str] = None
    nullable: bool = True
    null_action: str = None
    regex: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ColumnConfig':
        return ColumnConfig(
            name=d['name'],
            type=d['type'],
            format=d.get('format'),
            nullable=d.get('nullable', True),
            null_action=d['null_action'],
            regex=d.get('regex'),
            min=d.get('min'),
            max=d.get('max')
        )

@dataclass
class AcquisitionTableConfig:
    """
    Configuration for a single table in the acquisition layer, including
    column definitions, primary key, and scheduling metadata.
    """
    name: str
    attribute: Optional[str]
    primary_key: List[str]
    columns: List[ColumnConfig]
    injestor: str
    frequency: str
    release_day_rule: str
    release_time: str
    timezone: str

    @staticmethod
    def from_dict(d: Dict[str, Any], defaults: Dict[str, Any]) -> 'AcquisitionTableConfig':
        # Inherit defaults when not explicitly overridden
        injestor = d.get('injestor', defaults.get('injestor'))
        frequency = d.get('frequency', defaults.get('frequency'))
        release_day_rule = d.get('releaseDayRule', defaults.get('releaseDayRule'))
        release_time = d.get('releaseTime', defaults.get('releaseTime'))
        timezone = d.get('timezone', defaults.get('timezone'))

        return AcquisitionTableConfig(
            name=d['name'],
            attribute=d.get('attribute'),
            primary_key=d.get('primaryKey', []),
            columns=[ColumnConfig.from_dict(c) for c in d.get('columns', [])],
            injestor=injestor,
            frequency=frequency,
            release_day_rule=release_day_rule,
            release_time=release_time,
            timezone=timezone
        )

@dataclass
class AcquisitionConfig:
    """
    Top-level configuration object that includes defaults and
    a list of table-specific configs.
    """
    defaults: Dict[str, Any]
    tables: List[AcquisitionTableConfig]
   
    def table_names(self) -> list[str]:
        return [t.name for t in self.tables]
    
    @staticmethod
    def load_from_file(path: str) -> 'AcquisitionConfig':
        """
        Load the acquisition configuration from a JSON file.
        """
        with open(path, 'r') as f:
            data = json.load(f)

        defaults = data.get('defaults', {})
        tables = [
            AcquisitionTableConfig.from_dict(tbl, defaults)
            for tbl in data.get('tables', [])
        ]

        return AcquisitionConfig(defaults=defaults, tables=tables)

from dataclasses import dataclass
import json

    
@dataclass(frozen=True)
class ConsolidateColumnConfig:
    in_name: str
    out_name: str
    type: str

    @classmethod
    def from_dict(cls, d: dict) -> "ConsolidateColumnConfig":
        return cls(**d)
    
    @classmethod
    def load_from_file(cls, path: str) -> "ConsolidateColumnConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

@dataclass(frozen=True)
class ConsolidationTableConfig:
    name: str
    columns: list[ConsolidateColumnConfig]

    def table_names(self) -> list[str]:
        return [self.name in self]

    def in_names(self) -> list[str]:
        return [col.in_name for col in self.columns]

    def in_to_out_map(self) -> dict[str, str]:
         return {col.in_name: col.out_name for col in self.columns}

    def date_out_names(self) -> list[str]:
        return [col.out_name for col in self.columns if col.type == "date"]

    def number_out_names(self) -> list[str]:
        return [col.out_name for col in self.columns if col.type == "number"]
    
    @classmethod
    def from_dict(cls, d: dict) -> "ConsolidationTableConfig":
        cols = [ConsolidateColumnConfig.from_dict(c) for c in d["columns"]]
        return cls(name=d["name"], columns=cols)

    @classmethod
    def load_from_file(cls, path: str) -> list["ConsolidationTableConfig"]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [cls.from_dict(item) for item in data]

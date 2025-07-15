from dataclasses import dataclass

@dataclass
class ColumnConfig:
    in_name: str
    out_name: str
    type: str

@dataclass
class TableConfig:
    name: str
    columns: list[ColumnConfig]

    def in_names(self) -> list[str]:
        return [col.in_name for col in self.columns]

    def in_to_out_map(self) -> dict[str, str]:
         return {col.in_name: col.out_name for col in self.columns}
    
    def date_out_names(self) -> list[str]:
        return [col.out_name for col in self.columns if col.type == "date"]
    
    def number_out_names(self) -> list[str]:
        return [col.out_name for col in self.columns if col.type == "number"]
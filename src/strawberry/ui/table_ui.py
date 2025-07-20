import json
from pandas import pd, st

class TableUI:


    def build(self, df: pd.DataFrame, config_path: str):
        # 1. Load the JSON description
        with open(config_path, "r") as f:
            config_json = json.load(f)

        # 2. Build Streamlit column_config objects dynamically
        column_config = {}
        for col_name, props in config_json.items():
            col_type = props.get("type")
            label    = props.get("label", "")
            help_txt = props.get("help", "")
            fmt      = props.get("format", "")

            if col_type == "DateColumn":
                column_config[col_name] = st.column_config.DateColumn(
                    label=label, help=help_txt, format=fmt
                )
            elif col_type == "NumberColumn":
                column_config[col_name] = st.column_config.NumberColumn(
                    label=label, help=help_txt, format=fmt
                )
            else:
                # fallback to default – you could raise here if it's unexpected
                column_config[col_name] = st.column_config.Column(
                    label=label, help=help_txt
                )

        # 3. Derive display order from the JSON keys
        display_cols = [c for c in config_json.keys() if c in df.columns]

        # 4. Render the dataframe
        st.dataframe(
            df[display_cols],
            column_config=column_config,
            column_order=display_cols,
        )

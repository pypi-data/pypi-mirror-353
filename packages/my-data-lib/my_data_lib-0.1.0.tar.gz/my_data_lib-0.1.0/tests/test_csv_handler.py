import pandas as pd
from my_data_lib.csv_handler import CSVHandler

def test_csv_handler_read_and_write(tmp_path):
    df_original = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    file_path = tmp_path / "dados.csv"

    handler = CSVHandler(str(file_path))
    handler.write(df_original)

    df_lido = handler.read()

    pd.testing.assert_frame_equal(df_original, df_lido)

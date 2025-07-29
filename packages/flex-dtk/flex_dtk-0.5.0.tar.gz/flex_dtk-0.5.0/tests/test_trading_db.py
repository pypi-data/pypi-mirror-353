import pandas as pd
import pytest
from flex_dtk import trading_db


def test_query_returns_result_of_pandas_read_sql(monkeypatch):
    def dummy_df(*args, **kwargs) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": [1, 2, 3],
            }
        )

    monkeypatch.setattr(trading_db.pd, "read_sql", dummy_df)
    actual = trading_db.query(
        "SELECT * FROM TABLE",
        server="server.cool",
        database="db",
        username="m3",
        password="s3cr3t!123",
    )
    assert set(actual.columns) == {"a", "b"}
    assert len(actual) == 3


def test_query_raises_value_error_if_no_datbase_info_or_connection_given() -> None:
    with pytest.raises(ValueError):
        trading_db.query("HELLO WORLD!")

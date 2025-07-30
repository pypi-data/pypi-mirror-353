import dateutil.tz
import numpy as np
import pandas as pd

from tradingo.sampling import get_ig_service


def get_activity_history(
    from_date,
    to_date,
    svc=None,
    **kwargs,
):
    """
    get activtiy history and return dataframe per asset
    """

    svc = svc or get_ig_service()

    act = svc.fetch_account_activity_by_date(
        from_date=pd.Timestamp(from_date),
        to_date=pd.Timestamp(to_date),
    )
    act["DateTime"] = (
        pd.to_datetime(act["date"] + " " + act["time"])
        .dt.tz_localize(dateutil.tz.tzlocal())
        .dt.tz_convert("utc")
    )

    return tuple(
        (
            data.set_index("DateTime")
            .sort_index()
            .drop(["date", "time", "period", "epic", "marketName"], axis=1)
            .replace("-", np.nan)
            .astype(
                {
                    "size": float,
                    "stop": float,
                    "limit": float,
                },
                errors="ignore",
            ),
            (epic,),
        )
        for epic, data in iter(act.groupby("epic"))
    )

from wrappers import in_out_debug
from datetime import datetime, timezone, timedelta
from app_config import app_config


@in_out_debug
def get_dates() -> dict[str, str]:
    dt_now = datetime.now(timezone.utc)

    dt_from = (
        dt_now - timedelta(
            hours=(app_config.news_delay_hours + app_config.news_period_hours),
            seconds=1
        )
    ).strftime(format="%Y-%m-%dT%H:%M:%S.000Z")

    dt_to = (
        dt_now - timedelta(
            hours=app_config.news_delay_hours,
            seconds=1
        )
    ).strftime(format="%Y-%m-%dT%H:%M:%S.000Z")

    return {
        'from': dt_from,
        'to': dt_to
    }


if __name__ == "__main__":
    pass
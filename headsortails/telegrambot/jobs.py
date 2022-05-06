import datetime

from telegrambot.utils import add_coins


def every_day_job(job):
    """ Add coins to each account every day """
    time = datetime.time(hour=12, minute=12)
    job_daily = job.run_daily(
        add_coins,
        days=(0, 1, 2, 3, 4, 5, 6),
        time=time
    )

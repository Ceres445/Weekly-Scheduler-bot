from datetime import timedelta, datetime


def convert_format(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


def hour_rounder(t: datetime = datetime.now()):
    if t.minute < 30:
        return (t.replace(second=0, microsecond=0, minute=30, hour=t.hour) - t).total_seconds()
    else:
        return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
                + timedelta(hours=1) - t).total_seconds()

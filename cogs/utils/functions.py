from datetime import timedelta, datetime


def convert_format(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


def hour_rounder(t: datetime = datetime.now(), day: bool = False):
    if day:
        return (t.replace(second=0, microsecond=0, minute=0, hour=0) + timedelta(days=1) - t).total_seconds()
    else:
        if t.minute < 30:
            return (t.replace(second=0, microsecond=0, minute=30, hour=t.hour) - t).total_seconds()
        else:
            return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
                    + timedelta(hours=1) - t).total_seconds()


def get_pings(attendees: str):
    if attendees == 'int':
        return f"<@&815982951946125363>"
    elif attendees == 'crp':
        return f"<@&698791878421774397>"
    else:
        return f"<@&815982951946125363>" + f"<@&698791878421774397>"


def get_attendee_name(param):
    if param == 'int':
        return 'Integrated'
    elif param == 'crp':
        return "CRP"
    else:
        return param


def get_name(a):
    if a == 1:
        return 'today'
    elif a == 2:
        return 'in five days'
    else:
        return 'in two days'


def get_days(date: datetime.date):
    if date == datetime.now().date():
        return 'today'
    else:
        return f'in {(date - datetime.now().date()).days} days'
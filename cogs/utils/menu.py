from discord.ext import menus
from tabulate import tabulate

from cogs.utils.functions import get_attendee_name


class ExamMenu(menus.MenuPages):
    def __init__(self, data):
        super().__init__(source=Source(data, key=lambda x: x['attendees'], per_page=6), clear_reactions_after=True)


class Source(menus.GroupByPageSource):
    def format_page(self, menu: ExamMenu, entry):
        test_data = sorted(list(entry)[1], key=lambda x: x['date'])
        converted = [(record['pid'], record['subject'], record['date'],
                      get_attendee_name(record['attendees'])) for record in test_data]

        string = tabulate(converted)
        return f'```prolog\n{string}\n```'

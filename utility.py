"""
utility.py
"""

import calendar

_month_numbers = dict((v,k) for k,v in enumerate(calendar.month_abbr))

def month_number(month):
    return _month_numbers[month]
from datetime import datetime, timedelta

days = ['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС']

def get_date(day_name):
    today = datetime.now().date()
    start = today - timedelta(days=today.weekday())
    dates = [start + timedelta(days=i) for i in range(7)]
    x = 0
    for i in days:
        if i == day_name:
            return dates[x]
        x+=1

print(get_date('ВС'))
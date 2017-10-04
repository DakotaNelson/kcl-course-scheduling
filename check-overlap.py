""" given a database of events (lectures, seminars) and my schedule,
attempt to determine which modules I'm able to attend
still VERY SLOPPY but it mostly works"""

import dataset

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

my_schedule = [
    {"day": "Mon", "start_time": "1500", "end_time": "1730"},
    {"day": "Tue", "start_time": "1000", "end_time": "1300"},
    {"day": "Tue", "start_time": "1400", "end_time": "1500"},
    {"day": "Tue", "start_time": "1600", "end_time": "1800"},
    {"day": "Wed", "start_time": "1200", "end_time": "1300"},
    {"day": "Thu", "start_time": "900", "end_time": "1230"},
    {"day": "Fri", "start_time": "900", "end_time": "1230"},
    {"day": "Fri", "start_time": "1300", "end_time": "1400"}
]

def clean_time(time_string):
    """ turns e.g. 10:00 into 1000 """
    return int(time_string.replace(":", ""))

def event_clashes(lecture):
    """ given an event, returns true if it clashes with my schedule """
    relevant_events = [e for e in my_schedule if e['day'] == lecture['day']]
    for event in relevant_events:
        lecture_start = clean_time(lecture['start_time'])
        lecture_end = clean_time(lecture['end_time'])
        event_start = clean_time(event['start_time'])
        event_end = clean_time(event['end_time'])
        if lecture_start >= event_start and lecture_start <= event_end:
            return True
        if lecture_end >= event_start and lecture_end <= event_end:
            return True
    return False


db = dataset.connect('sqlite:///schedule.db')

#results = db.query('SELECT * FROM events WHERE type is "Lecture";')
results = db.query('SELECT * FROM events;')

courses = db['courses'].distinct('code')

for course in courses:
    works = True

    lecture_events = db['events'].find(course_code=course['code'], type="Lecture")
    seminar_events = db['events'].find(course_code=course['code'], type="Seminar")

    lectures = list(lecture_events)
    seminars = list(seminar_events)

    if len(lectures) > 0:
        for lecture in lectures:
            if event_clashes(lecture):
                # DISQUALIFIED
                works = False
    else:
        for seminar in seminars:
            if event_clashes(seminar):
                # DISQUALIFIED
                works = False

    title = list(db['courses'].find(code=course['code']))[0]['title']
    if works:
        print(bcolors.OKGREEN + title + bcolors.ENDC)
    else:
        print(bcolors.FAIL + title + bcolors.ENDC)

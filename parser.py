from datetime import datetime
from icalendar import Calendar, Event, Alarm
import re
import datetime

def main():
  raw_data = open("chrome.in", "r")

  HEADER_STRING = "Show Waitlisted Classes"
  COURSE_DETAILS = "Class Nbr	Section	Component	Days & Times	Room	Instructor	Start/End Date"
  FOOTER_STRING = "Printer Friendly Page"
  
  load_data = [row.rstrip('\n') for row in raw_data]
  i = 0
  parsed_schedule = {}
  current_course = ""

  # skip the header
  while i < len(load_data):
    if load_data[i] == HEADER_STRING:
      i += 1
      break
    i += 1

  while i < len(load_data):
    # end of course data
    if load_data[i] == FOOTER_STRING:
      break

    # parse the course name
    if re.search(r"[A-Z]+ \d+[A-Z]* - .*", load_data[i]):
      current_course = load_data[i]
      parsed_schedule[current_course] = {'Events': [], 'Course Code': current_course.split(' - ')[0], 'Course Name': current_course.split(' - ')[1]}
      while i < len(load_data):
        if load_data[i] == COURSE_DETAILS:
          i += 1
          break
        i += 1

    # parse the class times
    class_number = load_data[i]
    section = load_data[i + 1]
    component = load_data[i + 2]
    parsed_schedule[current_course]['Events'].append({'Class Number': class_number, 'Section': section, 'Component': component,
    'Times': load_data[i + 3], 'Room': load_data[i + 4], 'Instructor': load_data[i + 5], 'Start End Date': load_data[i + 6]})
    i += 7
    while load_data[i].strip() == '':
      parsed_schedule[current_course]['Events'].append({'Class Number': class_number, 'Section': section, 'Component': component,
      'Times': load_data[i + 3], 'Room': load_data[i + 4], 'Instructor': load_data[i + 5], 'Start End Date': load_data[i + 6]})
      i += 7

  cal = Calendar()
  for _k, v in parsed_schedule.items():
    for e in v['Events']:
      # for every event
      if e['Times'] == 'TBA':
        print('tba date')
        continue
      # days of week, 0 = monday
      time_regex = re.search(r"([a-zA-Z]+) (.*)", e['Times'])
      m = list(map(int, list(time_regex.group(1).replace('F', '4').replace('Th', '3').replace('W', '2').replace('T', '1').replace('M', '0'))))
      
      [ds, de] = map(lambda x: datetime.datetime.strptime(x, "%m/%d/%Y"), e['Start End Date'].split(' - '))
      [ts, te] = time_regex.group(2).split(' - ')
      time_start_regex = re.search(r"(\d+):(\d+)(A|P)", ts)
      time_end_regex = re.search(r"(\d+):(\d+)(A|P)", te)
      
      # move to the first day of week
      while ds <= de:
        for dotw in m:
          # move to the correct date
          delta = dotw - ds.weekday()
          ds = ds + datetime.timedelta(days=delta if delta >= 0 else delta + 7)
          if ds <= de:
            event = Event()
            # alarm = Alarm()
            # alarm.add('trigger', datetime.timedelta(minutes=-10))
            # alarm.add('action', 'display')
            # alarm.add('description', 'reminder')
            # event.add_component(alarm)
            event.add('summary', f'{v["Course Code"]} ({e["Component"]})')
            event.add('description', f'{v["Course Code"]}-{e["Section"]}: {v["Course Name"]} ({e["Component"]}) with {e["Instructor"]}')
            event.add('location', e["Room"])
            event.add('dtstart', ds + datetime.timedelta(hours=int(time_start_regex.group(1)) + (12 if (time_start_regex.group(3) == 'P' and int(time_start_regex.group(1)) != 12) else 0), minutes=int(time_start_regex.group(2))))
            event.add('dtend', ds + datetime.timedelta(hours=int(time_end_regex.group(1)) + (12 if (time_end_regex.group(3) == 'P' and int(time_end_regex.group(1)) != 12) else 0), minutes=int(time_end_regex.group(2))))
            cal.add_component(event)
          else:
            break
        if len(m) == 1:
          ds = ds + datetime.timedelta(days=7)

  f = open('course_schedule.ics', 'wb')
  f.write(cal.to_ical())
  f.close()

main()

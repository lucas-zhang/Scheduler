import csv
import sys




class TourGuide:
  def __init__(self, name, tourTimes):
    #tourTimes is a list of TourTime objects
    self.name = name
    self.tourTimes = tourTimes

class TourTime:
  def __init__(self, day, hour, minute, isAM): 
    #Day is numbered 1-7; 1 being monday, isAM is true if it's am, false if pm
    self.day = day
    self.hour = hour
    self.minute = minute
    self.isAM = isAM

  # TourTime equals and not equals methods below
  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not self.__dict__ == other.__dict__
  

""" 
  *** Indices are 0 based *** 

  fNameColInd is the index of the first name column
  lNameColInd is the index of the last name column
  firstPrefInd is the index of the first preference column
  numPref is number of preferences
  startRowInd is the index of the first relevant row with information (not header rows)
"""


def readFile(file_string):
  data = []
  with open (file_string, 'rb') as f:
    reader = csv.reader(f)
    i = 0
    for row in reader:
      if i == 0:
        print(row)
        print(len(row))
      i += 1

  f.close()
  return data

def getTourGuides(data, startRowInd = 0, fNameColInd = 1, lNameColInd = 18, firstPrefInd = 13, numPref = 5):
  # Will return a list of TourGuide objects
  tourGuides = []
  dayMappings = {'Monday': 1, 'Tuesday' : 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}


  for i in range(startRowInd, len(data)):

    row = data[i]

    full_name = row[fNameColInd] + ' ' + row[lNameColInd]
    tourTimes = []

    for j in range(firstPrefInd, firstPrefInd + numPref):
      col = row[j] # A string of the first preference. For example "Saturday Morning Tour (11:00 AM)"
      dayNumber = dayMappings[col.split(' ', 1)[0]]
      timeString = col[col.index('(') + 1: col.rindex(')')] # "11:00 AM"
      hourString = timeString.split(':', 1)[0]
      restOfTimeString = hourString.split(' ', 1)
      minuteString = restOfTimeString[0]
      am_pm = restOfTimeString[1] #String either "AM" or "PM"

      tourTimes.append(TourTime(dayNumber, int(hourString), int(minuteString), am_pm.strip() == 'AM'))

    tourGuides.append(TourGuide(name, tourTimes))

    i += 1
  return tourGuides

def main():
  print('Main called')
  file_string = sys.argv[1];
  print(file_string)
  data = readFile(file_string)
  tourGuides = getTourGuides(data)

  for tourGuide in tourGuides:
    print tourGuide

if __name__ ==  '__main__':
  main()





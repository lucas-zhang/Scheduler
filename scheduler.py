import csv
import sys




class TourGuide:
  def __init__(self, firstName, lastName, tourTimes):
    #tourTimes is a list of TourTime objects
    self.firstName = firstName
    self.lastName = lastName
    self.tourTimes = tourTimes

  def getFullName(self):
    return self.firstName + ' ' + self.lastName

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
  with open (file_string, 'rU') as f:
    reader = csv.reader(f.read().splitlines())
    i = 0
    for row in reader:
      data.append(row)

  f.close()
  return data

def getTourGuides(data, startRowInd = 1, fNameColInd = 1, lNameColInd = 18, firstPrefInd = 13, numPref = 5):
  # Will return a list of TourGuide objects
  tourGuides = []
  dayMappings = {'Monday': 1, 'Tuesday' : 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}


  for i in range(startRowInd, len(data)):
    row = data[i]

    

    firstName = row[fNameColInd]
    lastName = row[lNameColInd]
    tourTimes = []

    for j in range(firstPrefInd, firstPrefInd + numPref):
      col = row[j].strip() # A string of the first preference. For example "Saturday Morning Tour (11:00 AM)"
      #print("The col string is: " + col)
      #print(i,j)
      if len(col) == 0 or (col.split(' ', 1)[0].strip() not in dayMappings.keys()): #if blank preference or not a tour date (i.e. studying abroad) 

        tourTimes.append(None) #optional line, only needed if we need to keep track of the number of preference
        continue

      
      dayString = col.split(' ', 1)[0].strip()
      timeString = col[col.index('(') + 1: col.rindex(')')].strip() # "11:00 AM"

      print(firstName + ' ' + lastName + ': ' + dayString + ', ' + timeString)
      timeStringArray = timeString.split(':', 1) #An array with elements of strings before and after colon i.e. ['11', '00 AM']
      afterColonArray = timeStringArray[1].split(' ', 1) #An array with elements of strings after the colon i.e. ['00', 'AM']

      hourString = timeStringArray[0].strip()
      minuteString = afterColonArray[0].strip()
      am_pm = afterColonArray[1].strip() #String either "AM" or "PM"


      tourTimes.append(TourTime(dayMappings[dayString], int(hourString), int(minuteString), am_pm.strip() == 'AM'))

    tourGuides.append(TourGuide(firstName, lastName, tourTimes))

    i += 1
  return tourGuides

def main():
  file_string = sys.argv[1];
  data = readFile(file_string)
  tourGuides = getTourGuides(data)

  for tourGuide in tourGuides:
    print(tourGuide.firstName, tourGuide.lastName,  [(tourTime.day, tourTime.hour, tourTime.minute, tourTime.isAM) for tourTime in tourGuide.tourTimes if tourTime])
    print('\n')

if __name__ ==  '__main__':
  main()





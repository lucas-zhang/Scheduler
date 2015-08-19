import csv
import sys

class TourGuide:
  def __init__(self, firstName, lastName, tourTimes):
    #tourTimes is a list of TourTime objects
    self.firstName = firstName
    self.lastName = lastName
    self.tourTimes = tourTimes


  def __repr__(self):
    #for nice formatting when you print it
    return self.jsonishPrint()

  def normalPrint(self):
    return self.getFullName() + ': ' + str([tourTime for tourTime in self.tourTimes if tourTime])

  def jsonishPrint(self):
    tourTimesString = ''
    for i, tourTime in enumerate(self.tourTimes):
      if tourTime:
        tourTimesString += (str(tourTime)) 
      
        tourTimesString += '\n'
        if i != self.countTourTimes() - 1:
          tourTimesString += '    '

      
    if tourTimesString == '':
      return '{' + '\n' + '    ' + 'Name: ' + self.getFullName() + '\n' + tourTimesString + '}'

    return '{' + '\n' + '    ' + 'Name: ' + self.getFullName() + '\n' + '    ' + tourTimesString + '}'


  def getFullName(self):
    return self.firstName + ' ' + self.lastName 

  def countTourTimes(self):
    count = 0
    for tourTime in self.tourTimes:
      if tourTime:
        count += 1
    return count

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

  def __repr__(self):
    reverseDayMappings = {1:'Monday', 2: 'Tuesday', 3: 'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday', 7:'Sunday'}
    am_pmMappings = {True: 'AM', False: 'PM'}
    return reverseDayMappings[self.day] + ' ' + str(self.hour) + ':' + "{0:0=2d}".format(self.minute) + ' ' + am_pmMappings[self.isAM]
  

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
  print(len(data))
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
  print('The python version we\'re using is ' + sys.version)
  file_string = sys.argv[1];
  data = readFile(file_string)
  tourGuides = getTourGuides(data)
  tourGuides.sort(key= lambda tourGuide: tourGuide.countTourTimes())
  for tourGuide in tourGuides:
    print(tourGuide)
    print('\n')


if __name__ ==  '__main__':
  main()





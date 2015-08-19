import csv
import sys
import random


class Assignment:
  #Similar to tourguide object, but it now has one assigned tourtime
  def __init__(self, firstName, lastName, assignedTourTime):
    #tourTimes is a list of TourTime objects
    self.firstName = firstName
    self.lastName = lastName
    self.assignedTourTime = assignedTourTime

  def __repr__(self):
    return '{\n        Assignment\n\n    Name: ' + self.firstName + ' ' + self.lastName + '\n    ' + 'Time: ' + str(self.assignedTourTime) + '\n\n}'

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
      return '{\n    ' + 'Name: ' + self.getFullName() + '\n' + tourTimesString + '}'

    return '{\n    ' + 'Name: ' + self.getFullName() + '\n    ' + tourTimesString + '}'


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

  def __hash__(self):
    return hash((self.day, self.hour, self.minute, self.isAM))

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

def getPreferenceGroups (tourGuides, numPrefCols = 5):
  #prefGroups is an array of arrays that stores an array of tourGuide objects at each index corresponding to 
  #the tourGuides amount of preferences. For example all tourGuides with 2 preferences will be at index 2

  prefGroups = [None] * (numPrefCols + 1)
  for tourGuide in tourGuides:
    numTourGuidePref = tourGuide.countTourTimes()

    if not prefGroups[numTourGuidePref]:
      prefGroups[numTourGuidePref] = []

    prefGroups[numTourGuidePref].append(tourGuide)

  return prefGroups


def getSortedTourTimesByFreq(prefGroup):
  #Gets tourtimes sorted by frequency, but with duplicates
  countsDict = {} #dictionary mapping tourTime objects to their counts
  for tourGuide in prefGroup:
    for tourTime in tourGuide.tourTimes:
      if tourTime:
        if tourTime in countsDict:
          countsDict[tourTime] += 1
        else:
          countsDict[tourTime] = 1

  countsArray = countsDict.items() #counts array is a list of tuples [(TourTime object, count)]
  countsArray.sort(key = lambda x: x[1]) #sorts


  sortedTourTimes = []
  for (tourTime, count) in countsArray:
    for i in range(count):
      sortedTourTimes.append(tourTime)

  return sortedTourTimes

def getTourTimeToGuideMapping(prefGroup):
  #generates a dictionary mapping a TourTime to tuples with a TourGuide and its pref number who have the TourTime listed as a preference
  timeToGuideDict = {} 
  for tourGuide in prefGroup:
    for i, tourTime in enumerate(tourGuide.tourTimes):
      if tourTime:
        if tourTime not in timeToGuideDict:
          timeToGuideDict[tourTime] = []
        timeToGuideDict[tourTime].append((tourGuide, i + 1))

  return timeToGuideDict


def chooseRandomly(collection):
  numItems = len(collection)
  chosen_index = random.randint(0, numItems - 1)

  return collection[chosen_index]



def generateAssignments(prefGroups, distribution = None):
  #distribution is a dictionary mapping a tourtime object
  assignments = [] #list of assignment objects
  tourGuidesNotAssigned = prefGroups[0]
  assigned = set([]) #set of assigned tourGuides
  for prefGroupNum, prefGroup in enumerate(prefGroups):
    if not prefGroup:
      continue

    sortedTourTimes = getSortedTourTimesByFreq(prefGroup)
    timeToGuideDict = getTourTimeToGuideMapping(prefGroup)

    for tourTime in sortedTourTimes: #sorted by frequency
      guidePrefTuples = [(tourGuide, prefNum) for (tourGuide, prefNum) in timeToGuideDict[tourTime] if tourGuide not in assigned] #list of tuples (TourGuide, Preference number)

      if len(guidePrefTuples) == 0:
        continue
      if len(guidePrefTuples) == 1: #if there's only one person that wants this TourTime in this prefGroup
        selTourGuide = guidePrefTuples[0][0]
        
      else: #if there are multiple people that want this tourtime

        minPrefNum = min(guidePrefTuples, key = lambda x: x[1])[1]
        highestPrefGuides = [tourGuide for (tourGuide, prefNum) in guidePrefTuples if prefNum == minPrefNum] #List of tuples with only the TourGuides with highest preference for this TourTime

        if len(highestPrefGuides) == 1: #if there are no preference ties
          selTourGuide = highestPrefGuides[0]

        else:
          selTourGuide = chooseRandomly(highestPrefGuides)

      assigned.add(selTourGuide)
      assignments.append(Assignment(selTourGuide.firstName, selTourGuide.lastName, tourTime))

  return (assignments, tourGuidesNotAssigned)






def main():
  print('The python version we\'re using is ' + sys.version)
  file_string = sys.argv[1];
  data = readFile(file_string)
  tourGuides = getTourGuides(data)

  prefGroups = getPreferenceGroups(tourGuides)
  assignments, unassigned = generateAssignments(prefGroups)

  for assignment in assignments:
    print (assignment)

  print ('We found a schedule with ' + str(len(assignments)) + ' assignments. They are listed above.\n\n')

  print('\nThere were ' + str(len(unassigned)) + ' unassigned tour guides. They are listed below.\n')
  for tourGuide in unassigned:
    print(tourGuide)

  




if __name__ ==  '__main__':
  main()





import csv
import sys
import random
import json
import re

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
  def __init__(self,eventName, day, hour, minute, isAM, maxAllowed): 
    #Day is numbered 1-7; 1 being monday, isAM is true if it's am, false if pm
    self.eventName = eventName
    self.day = day
    self.hour = hour
    self.minute = minute
    self.isAM = isAM
    self.maxAllowed = maxAllowed

  # TourTime equals and not equals methods below
  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __hash__(self):
    return hash((self.eventName, self.day, self.hour, self.minute, self.isAM, self.maxAssigned))

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


def readCSVFile(file_string):
  data = []
  with open (file_string, 'rU') as f:
    reader = csv.reader(f.read().splitlines())
    i = 0
    for row in reader:
      data.append(row)

  f.close()
  return data

def readJSONFile(file_string):
  """JSON file should include: startRowInd, fNameColInd, lNameColInd, firstPrefColInd, numPrefCols 
     margin, leaveUnassigned, ideal_dist, outputTourNames
  """
  with open(file_string) as json_file:
    jsonConfig = json.load(json_file)
  json_file.close()

  return jsonConfig



def parseTimeString(timeStr):
  """Gets the day, hour, minute, and am/pm of the string in csv preference column"""

  if timeStr:
    timeStr = timeStr.strip()
    dayMappings = {'MONDAY': 1, 'TUESDAY' : 2, 'WEDNESDAY': 3, 'THURSDAY': 4, 'FRIDAY': 5, 'SATURDAY': 6, 'SUNDAY': 7}

    timePattern = "(?i)([0-9]|0[0-9]|1[0-9]|2[0-3])\s*:\s*([0-5][0-9])\s*(AM|PM)"
    dayPattern = "(?i)Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"

    dayMatch = re.search(dayPattern, timeStr)
    timeMatch = re.search(timePattern, timeStr)

    if not dayMatch or not timeMatch:
      return None

    day = dayMappings[dayMatch.group().upper()]
    hour = int(timeMatch.groups()[0])
    minute = int(timeMatch.groups()[1])
    isAM = timeMatch.groups()[2].upper()

    return (day, hour, minute, isAM)


  else:
    return None

def createDistAndNameDict(jsonTimeObjects):
  #a jsonTimeObject are similar but NOT the same as tourtime objects

  distDict = {} #distDict maps (day, hour, minute, isAM) to (eventName, maxAssigned)  value for a time

  for jsonTimeObject in jsonTimeObjects:
    day = jsonTimeObject['day']
    hour = jsonTimeObject['hour']
    minute = jsonTimeObject['minute']
    isAM = jsonTimeObject['isAM']
    maxAllowed = jsonTimeObject['maxAllowed']
    eventName = jsonTimeObject['eventName']
    distDict[(day, hour, minute, isAM)] = (eventName, maxAllowed)

  return distDict


def getTourGuides(data, distDict, startRowInd = 1, fNameColInd = 1, lNameColInd = 18, firstPrefColInd = 13, numPrefCols = 5):
  # Will return a list of TourGuide objects
  tourGuides = []
  
  for i in range(startRowInd, len(data)):
    row = data[i]
    firstName = row[fNameColInd]
    lastName = row[lNameColInd]
    tourTimes = []

    for j in range(firstPrefColInd, firstPrefColInd + numPrefCols):
      col = row[j]# A string of the first preference. For example "Saturday Morning Tour (11:00 AM)"
      day, hour, minute, isAM = parseTimeString(col)
      eventName, maxAllowed = distDict[(day, hour, minute, isAM)]
      tourTimes.append(TourTime(eventName, day, hour, minute, isAM, maxAllowed))

    tourGuides.append(TourGuide(firstName, lastName, tourTimes))
    i += 1

  return tourGuides

def getAllTourTimes(tourGuides):
  tourTimes = set([])
  for tourGuide in tourGuides:
    for tourTime in tourGuide.tourTimes:
      if tourTime not in tourTimes:
        tourTimes.add(tourTime)

  return tourTimes


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
  #generates a dictionary mapping a TourTime to (TourGuide, prefNum) who have the TourTime listed as a preference within preference group
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


def getLeastFullTime(tourGuide, currAssignCounts):
  """ Gets the most available time of a TourGuide based off the most availabe spots left according 
      to maxAssigned
  """
  timeDiffTuples = [(tourTime, tourTime.maxAssigned - currAssignCounts[tourTime]) for tourTime in tourGuide.tourTimes]
  max_diff = max(timeDiffTuples, key = lambda t: t[1])[1]
  leastFullTimes = [tourTime for (tourTime, diff) in timeDiffTuples if diff == max_diff]

  return chooseRandomly(leastFullTimes)


def handleUnassigned(prefGroup, leaveUnassigned, assigned, tourGuidesNotAssigned, currAssignCounts):
  for tourGuide in prefGroup:
    if tourGuide not in assigned:
      if leaveUnassigned:
        tourGuidesNotAssigned.append(tourGuide)
      else:
        selTourTime = getLeastFullTime(tourGuide, currAssignCounts)
        assigned.add(tourGuide)
        assignments.append(Assignment(tourGuide.firstName, tourGuide.lastName, selTourTime))
        currAssignCounts[selTourTime] += 1

  return (assigned, tourGuidesNotAssigned, currAssignCounts)


def generateAssignments(prefGroups, currAssignCounts,  margin = 0, leaveUnassigned = True):
  """
    margin is the amount we can go over distribution
    ideal_dist is a dictionary mapping a tourtime object

    leaveUnassigned is a boolean indicating whether or not to assign unassigned tourguides at 
    the end of each pref group. If leaveUnassigned is false, we'll assign each unassigned tourGuide
    at the end to a tourtime to the tourtime with the most available spots (ideal_dist - curr_dist)

  """

  assignments = [] #list of assignment objects
  tourGuidesNotAssigned = prefGroups[0]
  assigned = set([]) #set of assigned tourGuides

  for prefGroupNum, prefGroup in enumerate(prefGroups):
    if not prefGroup:
      continue

    if prefGroupNum == 0:
      continue

    sortedTourTimes = getSortedTourTimesByFreq(prefGroup)
    timeToGuideDict = getTourTimeToGuideMapping(prefGroup)

    for tourTime in sortedTourTimes: #sorted by frequency
      if tourTime.currAssigned >= (currAssignCounts[tourTime] + margin):
        continue

      guidePrefTuples = [(tourGuide, prefNum) for (tourGuide, prefNum) in timeToGuideDict[tourTime] if tourGuide not in assigned] #list of tuples (TourGuide, Preference number)

      if len(guidePrefTuples) == 0: #if there are no unassigned tourguides that want this tourtime
        continue

      #if there are one or more unassigned tourguides that want this tourtime
      minPrefNum = min(guidePrefTuples, key = lambda x: x[1])[1]
      highestPrefGuides = [tourGuide for (tourGuide, prefNum) in guidePrefTuples if prefNum == minPrefNum] #List of tuples with only the TourGuides with highest preference for this TourTime

      if len(highestPrefGuides) == 1: #if there are no preference ties
        selTourGuide = highestPrefGuides[0]

      else:
        selTourGuide = chooseRandomly(highestPrefGuides)

      assigned.add(selTourGuide)
      assignments.append(Assignment(selTourGuide.firstName, selTourGuide.lastName, tourTime))
      currAssignCounts[tourTime] += 1

    #Line below handles unassigned guides
    assigned, tourGuidesNotAssigned, currAssignCounts = handleUnassigned(prefGroup, leaveUnassigned, assigned, \
                                                                  tourGuidesNotAssigned, currAssignCounts)






  return (assignments, tourGuidesNotAssigned)


def generateOutputData(assignments, unassigned):
  return
def outputToCSV(file_string, outputData):
  with open (file_string, 'w') as f:
    writer = csv.writer(f)
    writer.writerows(outputData)


  f.close()
  return



def main():
  input_csv_string = sys.argv[1]
  json_file_string = sys.argv[2]
  output_csv_string = sys.argv[3]


  data = readCSVFile(input_csv_string)
  for (row in data):
    print (data)
  jsonConfigDict = readJSONFile(json_file_string)
  print(jsonConfigDict)

  distAndNameDict = createDistAndNameDict(jsonConfigDict['tour_times'])

  tourGuides = getTourGuides(data)
  prefGroups = getPreferenceGroups(tourGuides)
  tourTimes = getAllTourTimes(tourGuides) # a set
  currAssignCounts = dict.fromkeys(tourTimes, 0)
  assignments, unassigned = generateAssignments(prefGroups, 0, True, currAssignCounts)



if __name__ ==  '__main__':
  main()
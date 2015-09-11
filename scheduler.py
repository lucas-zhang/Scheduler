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
  def __init__(self, firstName, lastName, status, unassignedReason, tourTimes):
    #tourTimes is a list of TourTime objects
    self.firstName = firstName
    self.lastName = lastName
    self.status = status
    self.unassignedReason = unassignedReason
    self.tourTimes = tourTimes

  def __repr__(self):
    #for nice formatting when you print it
    return self.indentedPrint()

  def indentedPrint(self):
    tourTimesString = ''
    for i, tourTime in enumerate(self.tourTimes):
      tourTimesString += (str(i + 1) + ': ' + str(tourTime)) 
      tourTimesString += '\n'
      if i != len(self.tourTimes) - 1:
        tourTimesString += '        '

      
    if tourTimesString == '':
      return '{\n    ' + 'Name: ' + self.getFullName() + '\n    ' +  'Status: ' + \
              self.status + '\n    ' + 'Reason: ' + self.unassignedReason + '\n    ' +  \
              'Preferences: \n        '  + tourTimesString + '}'

    return '{\n    ' + 'Name: ' + self.getFullName() + '\n    ' + 'Status: ' +  self.status + \
     '\n    ' + 'Reason: ' + str(self.unassignedReason) + '\n    ' + \
     'Preferences: \n        ' + tourTimesString + '}'


  def getFullName(self):
    return self.firstName + ' ' + self.lastName 

  def countTourTimes(self):
    count = 0
    for tourTime in self.tourTimes:
      if tourTime:
        count += 1
    return count

class TourTime:
  def __init__(self, eventName, day, hour, minute, isAM, maxAllowed): 
    #Day is numbered 1-7; 1 being monday, isAM is true if it's am, false if pm
    self.eventName = eventName
    self.day = day
    self.hour = hour
    self.minute = minute
    self.isAM = isAM
    self.maxAllowed = maxAllowed

  # TourTime equals and not equals methods below

  def convertToMinutes(self):
    #converts a tourtime object to seconds with Monday 12:00AM as 0
    if self.day is None or self.hour is None or self.minute is None or self.isAM is None:
      return sys.maxint
    hourMap = {} #maps (hour, isAM) -> hour in 24 hr time scheme
    hourMap[(12, True)] = 0
    hourMap[(12, False)] = 12

    for hour in range(1, 12):
      hourMap[(hour, True)] = hour
      hourMap[(hour, False)] = (hour + 12)

    return (self.day - 1) * 24 * 60 + hourMap[(self.hour, self.isAM)] * 60 + self.minute


  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __hash__(self):
    return hash((self.eventName, self.day, self.hour, self.minute, self.isAM, self.maxAllowed))

  def __ne__(self, other):
    return not self.__dict__ == other.__dict__

  def __repr__(self):
    reverseDayMappings = {1:'Monday', 2: 'Tuesday', 3: 'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday', 7:'Sunday'}
    am_pmMappings = {True: 'AM', False: 'PM'}

    if self.day is None and self.hour is None and self.minute is None and self.isAM is None:
      return 'Event name: ' + self.eventName + ' (You forgot to input a valid time!)'
    return reverseDayMappings[self.day] + ', ' + str(self.hour) + ':' + "{0:0=2d}".format(self.minute) + ' ' \
            + am_pmMappings[self.isAM] + ' (' + self.eventName + ')'

  
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
    isAM = timeMatch.groups()[2].upper() == 'AM'

    return (day, hour, minute, isAM)


  else:
    return None

def createDistAndNameDict(jsonTourObjects):
  #a jsonTourObject are similar but NOT the same as tourtime objects

  distDict = {} #distDict maps (day, hour, minute, isAM) to (eventName, maxAllowed)  value for a time

  for jsonTourObject in jsonTourObjects:
    timeTup = parseTimeString(jsonTourObject['time'])
    if not timeTup:
      continue
    day, hour, minute, isAM = timeTup
    maxAllowed = jsonTourObject['maxAllowed']
    eventName = jsonTourObject['eventName']
    distDict[(day, hour, minute, isAM)] = (eventName, maxAllowed)

  return distDict

def removeDuplicateTimes(tourTimes):
  noDuplicates = []
  counts = {}

  for tourTime in tourTimes:
    if tourTime:
      if tourTime not in counts:
        noDuplicates.append(tourTime)
        counts[tourTime] = 1
    else:   
      noDuplicates.append(None)
    
  return noDuplicates

def getTourGuides(csv_data, distAndNameDict, input_csv_dict):
  # Will return a list of TourGuide objects
  tourGuides = []

  startRowInd = input_csv_dict['startRowInd']
  fNameColInd = input_csv_dict['fNameColInd']
  lNameColInd = input_csv_dict['lNameColInd']
  firstPrefColInd = input_csv_dict['firstPrefColInd']
  numPrefCols = input_csv_dict['numPrefCols']
  statusColInd = input_csv_dict['statusColInd']


  for i in range(startRowInd, len(csv_data)): #loops over the rows
    row = csv_data[i]
    firstName = row[fNameColInd]
    lastName = row[lNameColInd]
    status = row[statusColInd]

    if firstName: 
      firstName = firstName.strip()
      firstName = firstName[0].upper() + firstName[1:]

    if lastName: 
      lastName = lastName.strip()
      lastName = lastName[0].upper() + lastName[1:]

    if status: status = status.strip()

    tourTimes = []

    for j in range(firstPrefColInd, firstPrefColInd + numPrefCols): #loops over preferences

      col = row[j]# A string of the first preference. For example "Saturday Morning Tour (11:00 AM)"

      timeTup = parseTimeString(col)

      if not timeTup:
        tourTimes.append(None)
        continue

      day, hour, minute, isAM = timeTup
      try: 
        eventName, maxAllowed = distAndNameDict[(day, hour, minute, isAM)]
      except KeyError:
        currTourTime = TourTime("", day, hour, minute, isAM, "")
        print(str(currTourTime) + " is in the csv, but not in the JSON! Please fix the csv or JSON. The first instance of this in row " + str(i) + ", column " + str(j) + " (0 indexed)!");
        sys.exit(1);
      tourTimes.append(TourTime(eventName, day, hour, minute, isAM, maxAllowed))

    uniqueTourTimes = removeDuplicateTimes(tourTimes)
    tourGuides.append(TourGuide(firstName, lastName, status, None, uniqueTourTimes))
    i += 1

  return tourGuides


def getAllTourTimes(tourGuides):
  tourTimes = set([])
  for tourGuide in tourGuides:
    for tourTime in tourGuide.tourTimes:
      if tourTime not in tourTimes:
        tourTimes.add(tourTime)

  return tourTimes


def getPreferenceGroups (tourGuides, numPrefCols):
  #prefGroups is an array of arrays that stores an array of tourGuide objects at each index corresponding to 
  #the tourGuides amount of preferences. For example all tourGuides with 2 preferences will be at index 2

  prefGroups = [[]] * (numPrefCols + 1)
  for tourGuide in tourGuides:
    numTourGuidePref = tourGuide.countTourTimes()
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
      to maxAllowed
  """
  timeDiffTuples = [(tourTime, tourTime.maxAllowed - currAssignCounts[tourTime]) for tourTime in tourGuide.tourTimes]
  max_diff = max(timeDiffTuples, key = lambda t: t[1])[1]
  leastFullTimes = [tourTime for (tourTime, diff) in timeDiffTuples if diff == max_diff]

  return chooseRandomly(leastFullTimes)


def handleUnassigned(prefGroup, leaveUnassigned, assigned, tourGuidesNotAssigned, currAssignCounts):
  for tourGuide in prefGroup:
    if tourGuide not in assigned:
      if leaveUnassigned:
        tourGuide.unassignedReason = 'No open spots according to the ideal distribution.'
        tourGuidesNotAssigned.append(tourGuide)
      else:
        selTourTime = getLeastFullTime(tourGuide, currAssignCounts)
        assigned.add(tourGuide)
        assignments.append(Assignment(tourGuide.firstName, tourGuide.lastName, selTourTime))
        currAssignCounts[selTourTime] += 1

  return (assigned, tourGuidesNotAssigned, currAssignCounts)


def generateAssignments(prefGroups, currAssignCounts,  margin, leaveUnassigned):
  """
    margin is the amount we can go over distribution
    ideal_dist is a dictionary mapping a tourtime object

    leaveUnassigned is a boolean indicating whether or not to assign unassigned tourguides at 
    the end of each pref group. If leaveUnassigned is false, we'll assign each unassigned tourGuide
    at the end to a tourtime to the tourtime with the most available spots (ideal_dist - curr_dist)

  """

  assignments = [] #list of assignment objects
  tourGuidesNotAssigned = prefGroups[0]
  for tourGuide in tourGuidesNotAssigned:
    tourGuide.unassignedReason = 'No preferences given.'
  assigned = set([]) #set of assigned tourGuides

  for prefGroupNum, prefGroup in enumerate(prefGroups):
    if prefGroupNum == 0:
      continue

    sortedTourTimes = getSortedTourTimesByFreq(prefGroup)
    timeToGuideDict = getTourTimeToGuideMapping(prefGroup)

    for tourTime in sortedTourTimes: #sorted by frequency
      if currAssignCounts[tourTime] >= (tourTime.maxAllowed + margin):
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

  return (assignments, assigned, tourGuidesNotAssigned)



def groupGuidesByAssignment(assignments):
  assignmentMapping = {}
  for assignment in assignments:
    fullName = assignment.firstName + ' ' + assignment.lastName
    if assignment.assignedTourTime not in assignmentMapping:
      assignmentMapping[assignment.assignedTourTime] = []

    assignmentMapping[assignment.assignedTourTime].append(fullName)

  return assignmentMapping



def generateTourTimeSlots(jsonTourObjects):
  outputTourTimes = []
  for jsonTourObject in jsonTourObjects:
    timeTup = parseTimeString(jsonTourObject['time'])
    if not timeTup:
      day, hour, minute, isAM = (None, None, None, None)
    else:
      day, hour, minute, isAM = timeTup

    maxAllowed = jsonTourObject['maxAllowed']
    eventName = jsonTourObject['eventName']

    outputTourTimes.append(TourTime(eventName, day, hour, minute, isAM, maxAllowed))

  return outputTourTimes

def generateUnassignedOutput(unassigned):
  #generates a list of (tourGuide name, status, unassignedReason) and sorts it
  unassignedTuples = []
  for tourGuide in unassigned:
    unassignedTuples.append((tourGuide.getFullName(), tourGuide.status, tourGuide.unassignedReason))

  return unassignedTuples

def generateHeaderRow(tourTimeSlots):
  headerRow = ['Unassigned Tour Guide', 'Status', 'Reason', None]
  for tourTimeSlot in tourTimeSlots: 
    headerRow.append(str(tourTimeSlot))

  return headerRow

def findMaxColLength(assignmentMapping, unassignedTuples):
  maxAssigned = 0 # the number of people assigned to the tourtime with the most people

  for tourTime in assignmentMapping:
    numAssigned = len(assignmentMapping[tourTime])
    if numAssigned > maxAssigned:
      maxAssigned = numAssigned

  return max(maxAssigned, len(unassignedTuples))

def generateOutputRows(assignments, unassigned, sortByFirst, toursList):
  output_rows = []

  assignmentMapping = groupGuidesByAssignment(assignments)
  unassignedTuples = generateUnassignedOutput(unassigned)

  if sortByFirst:
    assignedSort = lambda s: s
    unassignedSort = lambda t: t[0]

  else:
    assignedSort = lambda s: s.split(' ')[1]
    unassignedSort = lambda t: t[0].split(' ')[1]

  unassignedTuples.sort(key = unassignedSort)

  for k in assignmentMapping:
    assignmentMapping[k].sort(key = assignedSort)


  tourTimeSlots = generateTourTimeSlots(toursList)
  tourTimeSlots.sort(key = lambda tourTime: tourTime.convertToMinutes())

  headerRow = generateHeaderRow(tourTimeSlots)

  output_rows.append(headerRow)
  maxColLength = findMaxColLength(assignmentMapping, unassignedTuples)

  for i in range(maxColLength):
    curr_row = []
    for field in unassignedTuples[i]:
      curr_row.append(field)

    curr_row.append(None) #column break between unassigned and actual assigned
    for tourTimeSlot in tourTimeSlots:
      if tourTimeSlot in assignmentMapping and i < len(assignmentMapping[tourTimeSlot]): 
        curr_row.append(assignmentMapping[tourTimeSlot][i])
      else: #either the timeSlot has no assigned people to begin with or no assigned people left
        curr_row.append(None)

    output_rows.append(curr_row)

  return output_rows



    
def outputToCSV(file_string, outputData):
  with open (file_string, 'w') as f:
    writer = csv.writer(f)
    writer.writerows(outputData)
  f.close()
  return

def checkUniqueness(assigned, unassigned):
  for tourGuide in unassigned:
    if tourGuide in assigned:
      return False
  return True

def main():
  print("main entered")
  input_csv_string = sys.argv[1]
  output_csv_string = sys.argv[2]
  json_file_string = sys.argv[3]


  input_csv_data = readCSVFile(input_csv_string)
  jsonConfigDict = readJSONFile(json_file_string)



  distAndNameDict = createDistAndNameDict(jsonConfigDict['tours'])

  tourGuides = getTourGuides(input_csv_data, distAndNameDict, jsonConfigDict['input_csv_options'])
  prefGroups = getPreferenceGroups(tourGuides, jsonConfigDict['input_csv_options']['numPrefCols'])
  tourTimes = getAllTourTimes(tourGuides) # a set
  currAssignCounts = dict.fromkeys(tourTimes, 0)
  margin = jsonConfigDict['margin']
  leaveUnassigned = jsonConfigDict['leaveUnassigned']
  assignments, assigned, unassigned = generateAssignments(prefGroups, currAssignCounts, margin, leaveUnassigned)

  output_rows = generateOutputRows(assignments, unassigned, jsonConfigDict['sortByFirst'], jsonConfigDict['tours'])
  outputToCSV(output_csv_string, output_rows)




if __name__ ==  '__main__':
  main()
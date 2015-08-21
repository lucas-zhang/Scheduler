import json
import os.path
import sys
import re

rePattern = '^.+\.(json)$' #regex for .json

enterNewFileStr = '\nPlease enter a different file path with extension .json to receive output:'

def getNoOverwriteRes(path):
  return 'You did NOT want to overwrite ' + path + '. ' + enterNewFileStr

def getEnterValidRes(path):
  return 'Please enter a valid response (yes or no).\nThe file "' + path + \
        '" already exists.\nIf you continue, it will be overwritten.\nDo you want to continue? Enter yes or no:'

def getTemplateRes(overwrite, path):
  if overwrite:
    return 'Now creating your template. Overwriting ' + path + '...'

  return 'Now creating your template. No overwrite of ' + path + ' needed...'



class OverWriteState: # state after prompt says "Do you want to overwrite?"
  def handleInput(self, stdInput, currPath): 
    stdInput = stdInput.strip()

    if stdInput == 'yes':
      response = 'Are you sure you want to overwrite ' + currPath + '? Enter yes or no:'
      nextState = ConfirmOverWriteState()
      validPath = currPath

    elif stdInput == 'no':
      response = getNoOverwriteRes(currPath)
      nextState = EnterFileState()
      validPath = None

    else:
      response = getEnterValidRes(currPath)
      nextState = OverWriteState()
      validPath = currPath

    return (response, nextState, validPath)

  def isDone(self):
    return False

  def __repr__(self):
    return 'OverWriteState'



class EnterFileState: # state after prompt says "Please enter file"
  def handleInput(self, stdInput, currPath): #prevPath isn't used, but it's just there so I can call handleInput without knowing what state
    stdInput = stdInput.strip()

    if re.match(rePattern, stdInput): #if file is .json
      if os.path.isfile(stdInput):
        response = 'The file entered "' + stdInput + \
        '" already exists.\nIf you continue, it will be overwritten.\nDo you want to continue? Enter yes or no:'
        nextState = OverWriteState()
        validPath = stdInput

      else:
        response = getTemplateRes(False, stdInput)
        nextState = DoneState()
        validPath = stdInput

    else:
      response = 'The file you entered "' + stdInput + '" has no name or does not have extension .json.' + enterNewFileStr
      nextState = EnterFileState()
      validPath = None

    return (response, nextState, validPath)

  def isDone(self):
    return False

  def __repr__(self):
    return 'EnterFileState'

class ConfirmOverWriteState: # state after prompt says "Are you sure you want to overwrite again?"
  def handleInput(self, stdInput, currPath):
    stdInput = stdInput.strip()

    if stdInput == 'yes':
      response = getTemplateRes(True, currPath)
      nextState = DoneState()
      validPath = currPath


    elif stdInput == 'no':
      response = getNoOverwriteRes(currPath)
      nextState = EnterFileState()
      validPath = None

    else:
      response = getEnterValidRes(currPath)
      nextState = ConfirmOverWriteState()
      validPath = currPath

    return (response, nextState, validPath)


  def isDone(self):
    return False

  def __repr__(self):
    return 'ConfirmOverWriteState'

class DoneState:
  def isDone(self):
    return True

  def __repr__(self):
    return 'DoneState'



def createJsonData(numTours):
  booleanStr = False
  eventNameStr = "ENTER tour name IN DOUBLE QUOTES"
  timeStr = "ENTER tour time including the day IN DOUBLE QUOTES"


  jsonDict = {} 

  input_csv_options = {}
  optionKeys = ['startRowInd', 'fNameColInd', 'lNameColInd', 'firstPrefColInd', 'numPrefCols', 'statusColInd']

  for key in optionKeys:
    input_csv_options[key] = -1

  tours = []

  for i in range(numTours):
    tour = {}
    tour['eventName'] = eventNameStr
    tour['time'] = timeStr
    tour['maxAllowed'] = -1
    tours.append(tour)

  jsonDict['***PLACEHOLDER COMMENTS***'] = {}
  placeHolderDict = jsonDict['***PLACEHOLDER COMMENTS***']
  placeHolderDict['-numbers'] = 'The -1\'s are placeholders. You can change them, but keep them as numbers.'
  placeHolderDict['-true/false'] = 'The falses are placeholders. You can change them, but keep them as true or false' 
  placeHolderDict['-strings'] = 'Follow instructions in the string placeholders.'
  placeHolderDict['other'] = 'Deleting this \'***PLACEHOLDER COMMENTS***\' object is optional. It\'s here just f.y.i'
  jsonDict['input_csv_options'] = input_csv_options
  jsonDict['margin'] = -1
  jsonDict['leaveUnassigned'] = booleanStr
  jsonDict['sortByFirst'] = booleanStr
  jsonDict['tours'] = tours

  return jsonDict


def makeTemplate(path, jsonDict):
  with open(path, 'w') as f:
    json.dump(jsonDict, f, indent = 4, sort_keys = True)
  f.close()
  return



def main():
  enteredPath = sys.argv[1]
  try:
    numTours = int(sys.argv[2])
  except ValueError:
    numTours = 15

  absPath = os.path.normpath(os.path.join(os.getcwd(), enteredPath))


  curr_state = EnterFileState()
  validPath = None
  stdInput = enteredPath

  while True: 
    response, nextState, validPath = curr_state.handleInput(stdInput, validPath)
    print('\n' + response + '\n')

    if nextState.isDone():
      break

    stdInput = sys.stdin.readline()
    curr_state = nextState

  jsonDict = createJsonData(numTours)
  makeTemplate(validPath, jsonDict)

  print('Your template has been created. Check "' + validPath + '" to view it.') 







if __name__ ==  '__main__':
  main()



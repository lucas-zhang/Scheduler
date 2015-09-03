import json
import os.path
import sys
import re



enterNewFileStr = '\nPlease enter a different file path with extension .json to receive output:'
enterValidRes = 'Please enter a valid response (yes or no).'

getAbsPathErrorRes = lambda path: 'There was an issue trying to write to "' + path + '". "' \
                              + path + '" is an invalid absolute path name.'

def getNoWriteRes(path, overwrite):
  if overwrite:
    return 'You did NOT want to overwrite ' + path + '. ' + enterNewFileStr

  return 'You did not want to write (NO overwrite neede) json data to "' + path + '".\n' + enterNewFileStr


def getWarningRes(path, overwrite, isValid):
  overwriteRes = '\nThe file "' + path + \
        '" already exists.\nIf you continue, it will be overwritten.\nDo you want to continue? Enter yes or no:'

  normalWriteRes = '\nDo you want to write data to "' + path + \
        '"? No overwrite will be needed. Enter yes or no.'

  if not isValid:
    overwriteRes = enterValidRes + overwriteRes
    normalWriteRes = enterValidRes + normalWriteRes

  if overwrite:
    return overwriteRes 

  return normalWriteRes

def getTemplateRes(path, overwrite):
  if overwrite:
    return 'Now creating your template. Overwriting ' + path + '...'

  return 'Now creating your template. No overwrite of ' + path + ' needed...'

def getConfirmRes(path, overwrite):
  if overwrite:
    return 'Are you sure you want to overwrite ' + path + '? Enter yes or no:'

  return 'Are you sure you want to write data to "' + path + \
        '"? No overwrite will be needed. Enter yes or no.'



class OverWriteState: # state after prompt says "Do you want to overwrite?"
  def handleInput(self, stdInput, currPath): 
    stdInput = stdInput.strip()
    overwrite = True
    if stdInput == 'yes':
      response = getConfirmRes(currPath, overwrite)
      nextState = ConfirmOverWriteState()
      validPath = currPath

    elif stdInput == 'no':
      response = getNoWriteRes(currPath, overwrite)
      nextState = EnterFileState()
      validPath = None

    else:
      response = getWarningRes(currPath, overwrite, False)
      nextState = OverWriteState()
      validPath = currPath

    return (response, nextState, validPath)

  def isDone(self):
    return False

  def __repr__(self):
    return 'OverWriteState'



class EnterFileState: # state after prompt says "Please enter file"
  def handleInput(self, stdInput, currPath = None): #currPath isn't used, but it's just there so I can call handleInput without knowing what state
    stdInput = stdInput.strip()
    absPath = os.path.abspath(stdInput)
    rePattern = '^([^\s]*\.)(json)$' #regex for .json

    if re.match(rePattern, stdInput): #if file is .json
      if os.path.isfile(absPath):
        overwrite = True
        response = getWarningRes(stdInput, overwrite, True)
        nextState = OverWriteState()
        validPath = stdInput

      else: #either valid path, but doesn't exist yet or an absolute path that isn't valid (check later)
          overwrite = False
          response = getConfirmRes(stdInput, overwrite)
          nextState = ConfirmNormalWriteState()
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


class ConfirmNormalWriteState: #state after prompt says "Are you sure you want to write to the file, no overwrite needed?"
  def handleInput(self, stdInput, currPath):
    overwrite = False
    stdInput = stdInput.strip()

    if stdInput == 'yes':
      response = getTemplateRes(stdInput, overwrite)
      nextState = DoneState()
      validPath = currPath

    elif stdInput == 'no':
      response = getNoWriteRes(currPath, overwrite)
      nextState = EnterFileState()
      validPath = None

    else:
      response = getWarningRes(currPath, overwrite, False)
      nextState = ConfirmNormalWriteState()
      validPath = currPath

    return (response, nextState, validPath)
  def isDone(self):
    return False

class ConfirmOverWriteState: # state after prompt says "Are you sure you want to overwrite again?"
  def handleInput(self, stdInput, currPath):
    overwrite = True
    stdInput = stdInput.strip()

    if stdInput == 'yes':
      response = getTemplateRes(currPath, overwrite)
      nextState = DoneState()
      validPath = currPath


    elif stdInput == 'no':
      response = getNoWriteRes(currPath, overwrite)
      nextState = EnterFileState()
      validPath = None

    else:
      response = getWarningRes(currPath, overwrite, False)
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



def openStream(curr_state):
  validPath = None
  enteredPath = sys.argv[1]
  stdInput = enteredPath


  while True: 
    response, nextState, validPath = curr_state.handleInput(stdInput, validPath)
    print('\n' + response + '\n')

    if nextState.isDone():
      break

    stdInput = sys.stdin.readline()
    curr_state = nextState


  return validPath

def main():

  try:
    numTours = int(sys.argv[2])
  except ValueError:
    numTours = 15

  curr_state = EnterFileState()
  validPath = openStream(curr_state)


  jsonDict = createJsonData(numTours)
  makeTemplate(validPath, jsonDict)




  print('Your template has been created. Check "' + validPath + '" to view it.') 







if __name__ ==  '__main__':
  main()



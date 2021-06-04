import re
#import sets

# importera bibliotek utf 8 medmera
import codecs


def contains(theString, theQueryValue):
  return theString.find(theQueryValue) > -1

def alreadyFoundInSentence(code, foundList):
  for found in foundList:
    if contains(found, code):
      return 1
  return 0

def lenSort(x, y):
  return len(y) - len(x)

def extractTags(line):
  resline = line[:]
  reP = re.compile("<.*?>")
  res = re.findall(reP, resline)
  if res:
    for el in res:
      resline = resline.replace(el, "")# remove all tags
  return resline


#negationfile = codecs.open("negations-gr.txt", mode='r', encoding='utf-8')
#negationfile = open("utvaldanegationer.txt", "r")
negationfile = open("negationtriggers_norska.txt", "r", encoding='utf-8')
negationdict = {}

for negation in negationfile:
  negation = negation.strip()
  negationline = negation.split("\t")
  negationterm = negationline[0]
  #print negationterm
  negationdict[negationterm] = 0
  
 

def includesnegation(term):
  splitted = term.split(" ")
  for el in splitted:
#	if negationdict.has_key(el):
    if el in negationdict:
      return 1
  return 0


codelist = {}

disorderfilestring = "NorMedTermCondition.txt"
#disorderfilestring = "multi-allDisorders-no-stopword-pre-man.txt"
#disorderfilestring = "allDisorders-ICD-10-norsk.txt"
print("Använder "+disorderfilestring)
disorderfile = open(disorderfilestring, "r", encoding='utf-8')
for codeline in disorderfile:
  codeline = codeline.strip().lower()
  withoutcomma = codeline.replace(",","")
  if not includesnegation(codeline):
    codelist[codeline] = 0
    if withoutcomma != codeline:
      codelist[withoutcomma] = 0
#print codelist


findingfile = open("myWords.txt", "r", encoding='utf-8')
for codeline in findingfile:
  codeline = codeline.strip().lower()
  withoutcomma = codeline.replace(",","")
  if not includesnegation(codeline):
    codelist[codeline] = 0
    if withoutcomma != codeline:
      codelist[withoutcomma] = 0

#print "My words" + str(len(codelist))

annotateddisorderfile = open("dummy.txt", "r", encoding='utf-8') # empty dummy
for codeline in annotateddisorderfile:
    codeline = codeline.strip().lower()
    withoutcomma = codeline.replace(",","")
    if not includesnegation(codeline):
        codelist[codeline] = 0
        if withoutcomma != codeline:
            codelist[withoutcomma] = 0


#print codelist

print("Number of symptoms and diagnosis in the dictionary: " + str(len(codelist)))


def getSNOMEDPhrase(sentence):
  line = extractTags(sentence)
  line = line.strip()
  line = line.replace('\n', "")
  line = line.replace(',', " ,")
  line = line.replace('.', " .")
  line = line.replace(':', " :")
  line = line.replace('?', " ?")
  words = line.split(" ")
  alreadyFoundDiagnosesInSentence = []

  nrOfWords = len(words)
  currentFirstWord = 0
  while(currentFirstWord < nrOfWords):
    #print currentFirstWord
    for currentLastWord in range(nrOfWords, currentFirstWord, -1):
      joined = " ".join(words[currentFirstWord: currentLastWord])
      joined = joined.lower()
      #print codelist
      #if codelist.has_key(joined):
      if joined in codelist:
        #print("SENTENCE")
        #print(sentence)
        #print("joined") 	
        #print(joined)
        alreadyFoundDiagnosesInSentence = alreadyFoundDiagnosesInSentence + [joined]
        currentFirstWord = currentFirstWord + len(words[currentFirstWord: currentLastWord]) - 1
        break
    currentFirstWord = currentFirstWord + 1
  alreadyFoundDiagnosesInSentence =list(set(alreadyFoundDiagnosesInSentence))
  return alreadyFoundDiagnosesInSentence





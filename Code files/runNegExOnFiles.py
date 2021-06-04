#!/usr/bin/python
#  -*- coding: utf-8 -*-

# för att fixa problemet UnicodeDecodeError: 'ascii' codec can't decode byte 0xcc in position 12: ordinal not in range(128)
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

import csv
import fnmatch
import os
import sys
from collections import Counter
from tabulate import tabulate
import pandas as pd
import shutil

if len(sys.argv) != 2:
    print("usage: runNegExOnFiles.py '<path>'")
    print(len(sys.argv))
    sys.exit(1)

# print "path: " +  sys.argv[1]
filespath = sys.argv[1]

print("Norsk NegEx")

answer = input("This script will change all '*.txt' files in the directory \n'" + os.path.abspath(
    filespath) + "' and in all directories below that. Do you really want to do this? In that case press 'y' and return.  ")

if answer != 'y':
    print("terminating script")
    sys.exit(1)

from negex import *
from negexPreprocessingSNOMED import *

report_list = []
negated_list = []

def len_compare(x, y):
    return len(y) - len(x)

#conj_list = ["ikke(*) uten", "at(.*) ikke"]


def replaceConj(line):
    #reP2 = re.compile("ikke(.*?) uten")
    #reP2 = r'(?=.*?(ikke(.*?))) (?=.*?(uten|at(.*?) ikke))'
    reP1 = re.compile(r'ikke(\s+\S+){,2} uten')
    hits1 = re.findall(reP1, line)
    #reP2 = re.compile(r'at(.*?) ikke')
    #reP2 = re.compile(r'at(\s+\S+){,2} ikke')
    #hits2 = re.findall(reP2, line)
    reP3 = re.compile(r'siden(\s+\S+){,2} ikke')
    hits3 = re.findall(reP3, line)
    #reP4 = re.compile(r'ikke(\s+\S+){,2} ved')
    #hits4 = re.findall(reP4, line)
    reP7 = re.compile(r'ikke(\s+\S+){,2} effekt')
    hits7 = re.findall(reP7, line)
    reP8 = re.compile(r'ikke(\s+\S+){,2} før etter')
    hits8 = re.findall(reP8, line)
    reP9 = re.compile(r'ikke(\s+\S+){,2} men')
    hits9 = re.findall(reP9, line)
    #reP10 = re.compile(r'ingen(\s+\S+){,2} som')
    #hits10 = re.findall(reP10, line)
    reP11 = re.compile(r'ikke(\s+\S+){,2} som')
    hits11 = re.findall(reP11, line)
    reP12 = re.compile(r'ikke(\s+\S+){,2} sikker')
    hits12 = re.findall(reP12, line)
    if hits1:
        line = line.replace("uten", "uten_conj")
    #if hits2:
    #    line = line.replace("ikke", "at_conj")
    if hits3:
        line = line.replace("ikke", "no_neg_conj")
    #if hits4:
    #    line = line.replace("ikke", "no_neg")
    if hits7:
        line = line.replace("ikke", "no_neg_conj")
    if hits8:
        line = line.replace("ikke", "no_neg_conj")
    if hits9:
        line = line.replace("ikke", "no_neg_conj")
    #if hits10:
    #    line = line.replace("ingen", "no_neg_conj")
    if hits11:
        line = line.replace("ikke", "no_neg_conj")
    if hits12:
        line = line.replace("ikke", "no_neg_conj")
    return line


# def replaceConj1(line):
#     reP2 = re.compile(r"at(.*?) ikke")
#     hits = re.findall(reP2, line)
#     if hits:
#         line = line.replace("ikke", "uten_conj")
#     return line

# def replaceConj2(line):
#     reP2 = re.compile("siden(.*?) ikke")
#     hits = re.findall(reP2, line)
#     if hits:
#         line = line.replace("ikke", "ikke_conj2")
#     return line

def runNegexForFile(patientRecord):
    foundFindings = 0
    foundNegations = 0
    reportsfile = open(patientRecord, 'r', encoding = 'UTF-8')
    reports = reportsfile.readlines()
    reportsfile.close()
    print(patientRecord)
    # shutil.copy2(patientRecord,  patientRecord + ".negexbackup")
    utdatafil = patientRecord + ".negex"
    # utdatafil = patientRecord

    utdatafile = open(utdatafil, 'w', encoding='UTF-8')

    for row in reports:
        # Strip tog bort tecken efter "."
        # row = row.strip()
        # print("Row ",row)
        # fixar så att mailadresser ej blir splittade
        # abc@abc.com
        # sentences = row.split(".")
        sentences = re.split(r'\.\W', row)
        # print("Sentences ", sentences)
        for line in sentences:
            line = line.strip()
            # print(getSNOMEDPhrase(line.strip()))
            if line:
                # report = sorted(getSNOMEDPhrase(line.strip()), cmp=len_compare) #start to match the longest word
                # print("Före")
                # print(line)
                report = sorted(getSNOMEDPhrase(line.strip()), key=len, reverse=True)
                # print("report")
                # print(report)
                if report:
                    report_list.append(report)
                    foundFindings = foundFindings + len(report)
                    lineWithUtanReplaced = replaceConj(line.lower())
                    #lineWithUtanReplaced = replaceConj1(line.lower())
                    #lineWithUtanReplaced = replaceConj2(line.lower())
                    # to fix greek lowercase
                    # lineWithUtanReplaced = replaceConj(line.decode('utf8').lower())
                    tagger = negTagger(lineWithUtanReplaced, report, rules=irules, negP=False)
                    tagged = tagger.getNegTaggedSentence() + ". "
                    # tagged = tagger.getNegTaggedSentence()

                    for term in report:
                        oneWordTerm = term.replace(" ", " ")
                        # oneWordTerm = term.replace(" ", "_")
                        # print(tagged)
                        # tagged = tagged.replace("[NEGATED]"+term+"[NEGATED]", "[NEGATED]"+oneWordTerm+"[NEGATED]")
                        tagged = tagged.replace("<NEGATED>" + term + "<NEGATED>",
                                                "<NEGATED>" + oneWordTerm + "</NEGATED>")
                        tagged = tagged.replace("[NEGATED]" + term + "[NEGATED]",
                                                "<NEGATED>" + oneWordTerm + "</NEGATED>")
                        print("Tagged:", tagged)
                        if re.search("<NEGATED>" + oneWordTerm, tagged):
                            print("Negat tagged", oneWordTerm)
                            negated_list.append(oneWordTerm)
                        tagged = tagged.replace("[PHRASE]", "")
                        tagged = tagged.replace("[PREN]", "")
                        tagged = tagged.replace("[POST]", "")
                        tagged = tagged.replace("[PSEU]", "")
                       # if re.search("<NEGATED>", tagged):
                        #    negated_list.append(oneWordTerm)
                    #foundNegations = foundNegations + (float(tagged.count("<NEGATED>")) / 2)
                    foundNegations = foundNegations + (tagged.count("<NEGATED>"))
                    utdatafile.write(tagged)
                    # print(tagged)
                else:
                    utdatafile.write(line + ". ")
        utdatafile.write("\n")
    return foundFindings, foundNegations


print("Start Norsk NegEx ******************************")
# rfile = open(r'utvaldanegationer.txt')
rfile = open(r'negationtriggers_norska.txt')
irules = sortRules(rfile.readlines())

totalFoundFindings = 0
totalFoundNegations = 0
for root, dirnames, filenames in os.walk(filespath):
    for filename in fnmatch.filter(filenames, '*.txt'):
        if not filename.endswith(".code.txt"):
            fullName = os.path.join(root, filename)
            findings, negations = runNegexForFile(fullName)
            totalFoundFindings = totalFoundFindings + findings
            totalFoundNegations = totalFoundNegations + negations

print("totalFoundFindings " + str(totalFoundFindings))
# to remove float
totalFoundNegations = int(totalFoundNegations)
print("totalFoundNegations " + str(totalFoundNegations))

#print("Report list:", report_list)

#print("Negated list:", negated_list)
negated_list_cp = set(negated_list)
#
#print("Negated_list_cp:", negated_list_cp)

flattened_list = [y for x in report_list for y in x]
#print(flattened_list)
result = Counter(flattened_list)
#print("Report frequency:", result)

#flattened_list = [y for x in l for y in x]
#print(flattened_list)
flattened_list_cp = set(flattened_list)
result = Counter(flattened_list)
#print(result)

Counter_dic = []

tot_counter = 0
Counter = 0
for item in flattened_list_cp:
    for line in flattened_list:
        if re.search(r"\b{}\b".format(item), line):
            Counter+= 1
            tot_counter+=1
    #print(item,Counter)
    Counter_dic.append([item, Counter])
    Counter = 0

# Counter_dic_negated = []
#
# tot_counter = 0
# Counter = 0
# for item in negated_list_cp:
#     for line in negated_list:
#         if re.search(r"\b{}\b".format(item), line):
#             Counter+= 1
#             tot_counter+=1
#     #print(item,Counter)
#     Counter_dic_negated.append([item, Counter])
#     Counter = 0


#print(Counter_dic)

#Counter_dic_df = pd.DataFrame(Counter_dic, columns=['FIndings word', 'Count'])
#print(Counter_dic_df)
# Python code to sort the tuples using second element
# of sublist Inplace way to sort using sort()
def Sort(sub_li):
    #reverse = True sort in descending order
    # key is set to sort using second element of
    # sublist lambda has been used
    sub_li.sort(key=lambda x: x[1], reverse=True)
    return sub_li

#print (tabulate(Sort(Counter_dic), headers=["Findings  ord", "Count"]))


#print(tabulate(Sort(Counter_dic_negated), headers=["Negated  word", "Count"]))




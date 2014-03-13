
'''
to make .csv file from command line, run:
python -c 'from filterCriteria import resultsToCSV; print resultsToCSV()'
'''


#import nltk
import MySQLdb,jsonrpclib
import sys, re,random,os,time,string
from pprint import pprint
import csv, collections
from json import loads
import pickle
import copy

common_words = ['a', 'about', 'also', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'do', 'do', 'for', 'from', 'get', 'go', 'go', 'go', 'has', 'have', 'her', 'here', 'hers', 'him', 'his', 'I', 'if', 'in', 'into', 'is', 'is', 'it', 'it', "it's", 'its', 'like', 'look', 'me', 'of', 'on', 'on', 'onto', 'or', 'out', 'say', 'she', 'so', 'that', 'the', 'their', 'theirs', 'them', 'there', 'they', 'this', 'to', 'up', 'want', 'was', 'went', 'were', 'what', 'which', 'with', 'you', 'your', 'yours']

''' Given a binary string of the annotation, return a pair of lists, 
the first of which contains the size of strings of contiguous 0s,
and the second of which contains the sizes of strings of contiguous 1s'''
def rawAnn_to_lists(annotation):
	binStr = re.sub(r' ', '', annotation)
	binStr = binStr.encode()
	zeros = []  #array to hold strings with contiguous 0s
	ones  = []  #array to hold strings with contiguous 1s
	count = 1 #size of current contiguous str
	prevChar = binStr[0]
	for c in binStr[1: len(binStr)]: #for all but first char in annotation
		if c == prevChar:
			count = count+1 #add the char to the current str of same chars
		else:
			if c == '0': #previous str was 1s
				ones = ones + [count] #add the count to the ones list
			else: #previous str was 0s
				zeros = zeros + [count] #add the count to the zeros list
			prevChar = c
			count = 1
	return (zeros, ones)
		
''' get word count of binary string annotation '''
def bin_wordCount(annotation):
	return len(annotation.split())

def countCommonWords(annotation, doc_html):
	binList = annotation.split() #convert the binary str to a list
	binList = map(int, binList) #convert unicode chars to int
	doc = nltk.clean_html(doc_html) #remove html tags
	wordList = doc.split() #get doc as list of words
	count = 0 #number of pure common word annotations
	is_highlighted = False #if previous word was highlighted
	found_notcommon = False #if we found a not-common word in ann
	for i, word in enumerate(wordList):
		if is_highlighted:
			if found_notcommon: #disregard all successive words in this ann
				if binList[i] == 0: #end of annotation
					found_notcommon = False
					is_highlighted = False
				#else bypass all following words in this ann
			else: #only common words found so far
				if binList[i] == 0: #last annotation was all common words
						count = count + 1
						is_highlighted = False
				else: #binList[i] == 1, this word is also highlighted
					if not(word.lower() in common_words):
						found_notcommon = True
					#else continue finding common words
		else: #we are not in highlighted portion
			if binList[i] == 1:
				is_highlighted = True
				if not(word.lower() in common_words):
					found_notcommon = True
					common_ann = ''
	#check last annotation
	if is_highlighted and not(found_notcommon):
		count = count + 1
	return count


''' failcrit1 is 1 if average annotation is too long, 0 otherwise
	failcrit2 is 1 if the longest annotation is too long, 0 otherwise
	failcrit3 is 1 if the longest non-highlighted portion is too long, 0 otherwise
	failcrit4 is 1 if there are not enough highlighted words, 0 otherwise
'''
def filterResults():
	#CUT OFF VALUES FOR CRITERIA; change if necessary
	#average word length of a hilighted portion
	avgAnnLen_threshold = 3 
	#longest contiguous annotation
	longestAnn = 120 
	#longest contiguous non-highlighted portion as a fraction of total words 
	longestNotAnn_frac = 1./3. 
	#number of highlighted words divided by total num of words
	percentAnn = .05 
	#allowable count of common words
	common_ans = 2

	#get doc_id, annotation, and a_name (annotation id) from all docs
	db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator', passwd='Ann0tateTh!s', db='FrameAnnotation', charset='ascii')
	c=db.cursor()
	c.execute('SELECT Documents.doc_id, doc_html, annotation, a_name FROM Documents INNER JOIN Annotations ON Documents.doc_id = Annotations.doc_id INNER JOIN Annotators ON Annotators.a_id = Annotations.a_id WHERE Documents.doc_id >= 9 ORDER BY doc_id, a_name')
	rows=c.fetchall()

	if (len(rows) == 0):
		print("no annotations selected")
		return None
	result = []
	for row in rows:
		(doc_id, doc_html, annotation, a_name) = row #fetch values from database entry
		wordCount = float(bin_wordCount(annotation)) #number of total words in doc
		#zeros is list of sizes of contiguous non-highlighted portion
		#ones is list of sizes of contiguous annotations
		(zeros, ones) = rawAnn_to_lists(annotation)

		crit1 = int(float(sum(ones))/float(len(ones)) < avgAnnLen_threshold)
		crit2 = int(float(max(ones)) > longestAnn)
		crit3 = int(float(max(zeros)) / wordCount > longestNotAnn_frac)
		crit4 = int(float(sum(ones)) / wordCount < percentAnn)
		crit5 = int(float(countCommonWords(annotation, doc_html)) > common_ans)

		#add result to result array
		result = result + [(int(doc_id), a_name.encode(), crit1, crit2, crit3, crit4, crit5)]

	return result

'''
create a .csv file that contains results of filterResults()
'''
def resultsToCSV():
	results = filterResults()
	f = open('filterResults.csv', 'w')
	f.write('doc_id, a_name, avg annotation too long, annotation too long, length of non-highlighted portion too long, not enough words highlighted ')
	for entry in results:
		strEntry = str(entry)
		strEntry = strEntry[1:len(strEntry) - 1] #don't include parens from tuple
		f.write('\n' + strEntry)
	f.close()



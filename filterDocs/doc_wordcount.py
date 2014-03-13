''' count words in all documents '''


import nltk, MySQLdb,jsonrpclib
import sys, re,random,os,time,string
from pprint import pprint
import csv, collections
from json import loads
import pickle
import copy

outputFile = open('wordcounts.txt', 'w')
#get annotations for a given doc_id
#taken from fextractor.py
db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation', charset='ascii')
c=db.cursor()
c.execute('SELECT Documents.doc_id, Documents.doc_html from Documents INNER JOIN Annotations ON Documents.doc_id = Annotations.doc_id GROUP BY Documents.doc_id')
rows=c.fetchall()
if (len(rows) == 0):
  print('no docs found')

#do not include apostrophe as punctuation
punctuation = re.sub(r'(\')', "", string.punctuation)
punctuation_regex = re.compile('[%s]' % re.escape(punctuation))

for row in rows:
  (doc_id, doc_html) = row

  #annPairs = charAnn_to_AnnIndexList(char_annotation) #get ann indices
  doc=nltk.clean_html(doc_html) #clean html from original document
  doc = doc.encode() #convert from unicode to ascii
  doc = re.sub(r'(\')', "", doc) #take out apostrophes

  #replace punctuation by whitespace
  noPunc_doc = punctuation_regex.sub(' ', doc) 

  wordlen = len(noPunc_doc.split()) #count words, split by whitespace
  result = str(doc_id) + ', ' + str(wordlen) + '\n'
  outputFile.write(result) #update results array

def wc(stringofwords):
	#do not include apostrophe as punctuation
	punctuation = re.sub(r'(\')', "", string.punctuation)
	punctuation_regex = re.compile('[%s]' % re.escape(punctuation))
	noPunc_str = punctuation_regex.sub(' ', stringofwords)
	return len(noPunc_str.split())

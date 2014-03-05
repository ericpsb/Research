
import nltk, MySQLdb,jsonrpclib
import sys, re,random,os,time,string
from pprint import pprint
import csv, collections
from json import loads
import pickle
import copy

def filter():
      db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation', charset='ascii')
      c=db.cursor()
      #c.execute('set charset utf8')

      c.execute("SELECT doc_html from Documents WHERE doc_id = 9")
      doc_rows = c.fetchall()
      # print(len(doc_rows))
      # print(len(doc_rows[2]))
      # print(len(doc_rows[0][0]))
      text=nltk.clean_html(doc_rows[0][0])
      # text=doc_rows[0][0]
      # separate=text.split('\n',1)

      # print(text)

      c.execute('SELECT char_annotation, a_id from Annotations WHERE doc_id = 9')
      ann_rows=c.fetchall()
      print(len(ann_rows))
      print(len(ann_rows[0]))
      print(len(ann_rows[0][0]))

      print(ann_rows[0])
      print(ann_rows[0][0])
      print(ann_rows[0][0].split(".")[0])
      # num_ann=len(rows)

      print(doc_rows[0][0][207:323])
      print(text[207:323])
      print(text[347:362])
      
filter()






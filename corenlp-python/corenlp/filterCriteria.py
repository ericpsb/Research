import fextractor.py 

#get annotations for a given doc_id
#taken from fextractor.py
db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation', charset='ascii')
c=db.cursor()
c.execute('SELECT char_annotation, a_id from Annotations WHERE doc_id = %s'%(doc_id,))
rows=c.fetchall()
if (len(rows) == 0):
  print("no annotations selected with doc_id =%s"%(doc_id))
  return None 
for (i = 0; i < len(rows); i++):
  (char_annotation, ann_id) = rows[i]
  char_ans = char_annotation.split() #split on whitespace
  def splitOnPeriod(str): #split on period
    str.split('.')
  #split each annotation start-end pair by period, then convert to int from unicode
  charPairs = map(int, map(splitOnPeriod, char_ans))
  highlight_lens = []
  for (j = 0; j < len(charPairs); j++):
    if (len(charPairs[j] == 2)):
      highlight_lens[j] = charPairs[j][1] - charPair[j][0]
  #average character length of words
  avgLen[i] = sum(highlight_lens)/len(highlight_lens)


'''
  @param criteria: boolean function to evaluate docs 
  @param docs: list of doc_id's 
  return pair of doc lists (passCriteria, failCriteria)
  where 'passCriteria' is the list of docs in which criteria(doc) is true
  and   'failCriteria' is the rest of the docs that did not pass the criteria
'''
def filterDocs(criteria, docs):
  def not_criteria(doc): #complement/opposite of criteria
    return not(criteria(doc)) 
  passCriteria = filter(criteria, docs)
  failCriteria = filter(not_criteria, docs)
  return (passCriteria, failCriteria)


'''
return true if the average char-length of the annotations
in doc is less than avglen  
'''
def shortAnnotations(doc, avglen): 

  
  #for a range of characters that are highlighted, find number of words that are highlighted
  def annotationLength(char_annotation):
#get annotations for a given doc_id
#taken from fextractor.py
db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation', charset='ascii')
c=db.cursor()
c.execute('SELECT char_annotation, a_id from Annotations WHERE doc_id = %s'%(doc_id,))
rows=c.fetchall()
if (len(rows) == 0):
  print("no annotations selected with doc_id =%s"%(doc_id))
  return None 
for (i = 0; i < len(rows); i++):
  (char_annotation, ann_id) = rows[i]
  char_ans = char_annotation.split() #split on whitespace
  def splitOnPeriod(str): #split on period
    str.split('.')
  #split each annotation start-end pair by period, then convert to int from unicode
  charPairs = map(int, map(splitOnPeriod, char_ans))
  highlight_lens = []
  for (j = 0; j < len(charPairs); j++):
    if (len(charPairs[j] == 2)):
      highlight_lens[j] = charPairs[j][1] - charPair[j][0]
  #average character length of words
  avgLen[i] = sum(highlight_lens)/len(highlight_lens)
    

    #test that this actually returns correct number of words

'''
return a pair of doc lists (passCriteria, failCriteria)
where passCriteria is list of docs that pass all criteria
'''
def filterByCriteriaList(critList, docs):


'''
run classifer and compare results when 




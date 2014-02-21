import fextractor.py 

#get annotations for a given doc_id
#taken from fextractor.py
db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation', charset='ascii')
c=db.cursor()
c.execute('SELECT char_annotation, a_id from Annotations WHERE doc_id = %s'%(doc_id,))
rows=c.fetchall()

for row in rows:
  (char_annotation, ann_id) = row
  char_ans = char_annotation.split() #split on whitespace
  def splitOnPeriod(str): #split on period
    str.split('.')
  charPairs = map(splitOnPeriod, char_ans)
  for charPairs


'''
  @param bool criteria evaluates whether or not a doc passes a criteria
  @docs  list of doc_id's 
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
return true if the average word-length of the annotations
in doc is less than avglen  
'''
def shortAnnotations(doc, avglen): 
  #for a range of characters that are highlighted, find number of words that are highlighted
  def annotationLength(char_annotation):

  #count the number of spaces

  #test that this actually returns corret number of words

'''
return a pair of doc lists (passCriteria, failCriteria)
where passCriteria is list of docs that pass all criteria
'''
def filterByCriteriaList(critList, docs):


'''
run classifer and compare results when 




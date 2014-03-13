'''
from the good_ans.csv, 
update the validity of each annotation in 
the MySQL annotation table 
'''

import MySQLdb

#open csv file for reading
filename = 'good_ans.csv'
f = open(filename, 'r')


#open MySQL connection
db=MySQLdb.connect(
  host='eltanin.cis.cornell.edu', 
  user='annotator', 
  passwd='Ann0tateTh!s', 
  db='FrameAnnotation', 
  charset='ascii')
c=db.cursor() #cursor

#each line is of the form: doc_id, ann_id, valid
for line in f:
  line = line.split(',') #split each line by commas into array
  if len(line) == 3 and (line[0] != 'doc_id') and line[0] != '': #not the first or last line
    doc_id = line[0]
    a_name = line[1] #first value in each row is ann_id
    isValid = line[2]  #second value in each row is whether or not ann is valid
    update = ("""UPDATE Annotations INNER JOIN Annotators 
      ON Annotators.a_id = Annotations.a_id SET valid = """ + isValid +
      'WHERE a_name = \'' + a_name + '\' AND doc_id = ' + doc_id)
    print update

    c.execute(update)
    db.commit()

db.close()
f.close()
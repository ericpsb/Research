'''
from the good_ans.csv, 
update the validity of each annotation in 
the MySQL annotation table 
'''

#open csv file for reading
filename = 'good_ans.csv'
f = open(filename, 'r')

'''
#open MySQL connection
db=MySQLdb.connect(
  host='eltanin.cis.cornell.edu', 
  user='annotator', 
  passwd='Ann0tateTh!s', 
  db='FrameAnnotation', 
  charset='ascii')
c=db.cursor() #cursor
'''

for line in f:
  line = line.split(',') #split each line by commas into array
  ann_id = line[0] #first value in each row is ann_id
  if (len(ann_id) > 10) and len(line) >= 2: #not the first or last line
    isValid = line[1]  #second value in each row is whether or not ann is valid
    print ('UPDATE annotations SET valid = ' + isValid + ' WHERE ann_id = \'' + ann_id + '\' ')

    '''
    update = 'UPDATE annotations SET valid = ' + isValid + ' WHERE ann_id = \' ' + ann_id + ' \' '
    cursor.execute(update)
    db.commit()
    '''


#db.close()
f.close()
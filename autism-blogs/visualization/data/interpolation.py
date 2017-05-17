import datetime
import csv

structure = []
for i in range(64):
    structure.append({})

minweek = datetime.datetime.strptime('2003-06-22', '%Y-%m-%d').date()
maxweek = datetime.datetime.strptime('2016-07-03', '%Y-%m-%d').date()

tenureOffsets = {}
birthOffsets = {}

f = open('ag.csv', 'r')
# epsb
# grab the column header. we'll use this later when writing the interpolated file
header = f.readline()
header = header.rstrip('\n')

for line in f:
    explode = line.split(",")
    blogid = explode[0]
    index =  int(blogid) - 1
    week = explode[53].rstrip('\n')
    week = datetime.datetime.strptime(week, '%Y-%m-%d').date()
    # keep track of offsets, both the amount and the resulting date/week
    tenureWeek = explode[54].rstrip('\n')
    tenureWeek = datetime.datetime.strptime(tenureWeek, '%Y-%m-%d').date()
    tenureOffsets[index] = int(explode[51])
    birthWeek = explode[55].rstrip('\n')
    if birthWeek != 'NA':
        birthWeek = datetime.datetime.strptime(birthWeek, '%Y-%m-%d').date()
        birthOffsets[index] = int(explode[52])
    else:
        birthOffsets[index] = 'NA'

    # here come the topic proportions
    vector = explode[1:51]
    for j in range(len(vector)):
        vector[j] = float(vector[j])
    # make sure we keep the time offsets with this row
    vector.extend([tenureWeek, birthWeek])
    structure[index][week] = vector

zero = []
for i in range(50):
    # zero.append(0.0)
    # we want NAs where we weren't able to interpolate
    zero.append('NA')

#print structure
allDates = []
current = minweek
d = datetime.timedelta(days=7)
while current <= maxweek:
    allDates.append(current)
    current = current + d

# for blogDict in structure:
#     if blogDict != {}:
#         for date in allDates:
#             if date not in blogDict:
#                 blogDict[date] = zero
#print structure[0]


with open('interpolated.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # epsb
    # first row of csv needs to be a column header
    # writer.writerow(header.split(','))
    topic_column_names = []
    for i in range(1,51):
        topic_column_names.append("Topic%02d" % i)
    writer.writerow(['BlogIndex'] + ['Date'] + ['InterpolationLevel'] + topic_column_names + ['TenureShift'] + ['BirthShift'])

    for i in range(len(structure)):
        blogDict = structure[i]
        if blogDict != {}:
            for date in allDates:
                if date in blogDict:
                    # if there's no interpolation to be done, just keep the offset datses from blogDict
                    writer.writerow([i+1]+[date]+[0]+blogDict[date])
                else:
                    # since we'll need to interpolate, figure out what the offset dates are and include those, too
                    tenureWeek = (date - datetime.timedelta(days=tenureOffsets[i]))
                    # make sure it's still a Sunday
                    tenureWeek += datetime.timedelta( days = -1 * ((1 + tenureWeek.weekday()) % 7) )
                    birthWeek = 'NA'
                    if birthOffsets[i] != 'NA':
                        birthWeek = (date - datetime.timedelta(days=birthOffsets[i]))
                        birthWeek += datetime.timedelta( days = -1 * ((1 + birthWeek.weekday()) % 7) )

                    #ONE WAY LIMIT OF INTERPOLATION WINDOW
                    limit = 5

                    next = []
                    level = 0
                    nextWeek = date
                    while (level < limit):
                        level +=1
                        nextWeek = nextWeek + datetime.timedelta(days=7)
                        if (nextWeek in blogDict ):
                            next = blogDict[nextWeek]
                            break
                    
                    past = []
                    backward = 0
                    prevWeek = date
                    while (level < limit):
                        level +=1
                        backward +=1
                        prevWeek = prevWeek - datetime.timedelta(days=7)
                        if (prevWeek in blogDict):
                            past = blogDict[prevWeek]
                            break
                      

                    #Interp not possible
                    if (past==[] or next==[]):
                        writer.writerow([i+1]+[date]+[-1]+zero+[tenureWeek, birthWeek])
                    

                    else:
                        props = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
                        for ind in range(len(past) - 2): # the -2 is to skip the offset dates at the end
                            props[ind] = past[ind] + (backward*((next[ind]-past[ind])/(level)))
                        # remember to keep the offset dates, too
                        props.extend([tenureWeek, birthWeek])
                        writer.writerow([i+1]+[date]+[level]+props)








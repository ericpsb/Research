# import csv
# with open('ag.csv', 'rb') as f:
#     reader = csv.reader(f)
#     for row in reader:
#         print row

structure = []
for i in range(64):
	structure.append({})


f = open('ag.csv', 'r+')
# epsb
# grab the column header.
header = f.readline()
header = header.rstrip('\n')

for line in f:
	explode = line.split(",")
	blogid = explode[0]
	index =  int(blogid) - 1
	week = explode[51].rstrip('\n')
	vector = explode[1:51]
	structure[index][week] = vector

print structure

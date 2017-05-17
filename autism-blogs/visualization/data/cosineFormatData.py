# @author: epsb
# Format agTotal.csv (as output by visualizationBuilder.R) for the cosine visualization.
# Written for Python 3

# import csv
# with open('ag.csv', 'rb') as f:
#     reader = csv.reader(f)
#     for row in reader:
#         print row

structure = {}

f = open('agTotal.csv', 'r+')
# epsb
# grab the column header. these are the short names of the topics
header = f.readline()
header = header.rstrip('\n')

for line in f:
	explode = line.split(",")
	blogid = explode[0]
	index =  int(blogid) - 1
	vector = explode[1:]
	vector[-1] = vector[-1].rstrip('\n')
	structure[index] = vector

outf = open('../cosineData.js', 'w')

# overall averages of topics for each blog, sorted by blog
print("var data = " + str( [a[1] for a in sorted(structure.items())] ) + ";", file=outf)
# the list manipulation in the middle makes sure we get the average topic scores sorted by blogid

# names of topics
print("var topics = [" + header[header.index(',')+1:] + "];", file=outf)
# the treatment of header is due to the fact that it's still represented as a string, not as a list

outf.flush()
outf.close()
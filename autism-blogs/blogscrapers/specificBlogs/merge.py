import glob

ofile = open("merged_file.json", "w", encoding='utf-8')
ofile.write("[")
first = True
for f in glob.glob("Done/*/data.json"):
	with open(f, "r") as ifile:
        if first == True:
			first = False
		else:
			ofile.write(",")
		ofile.write(ifile.read())
ofile.write("]")
ofile.close()
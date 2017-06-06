import json
import re

docnum = 0;
with open("merged_file.json", "r", encoding='utf-8') as ifile:
	file = ifile.read()
filejson = json.loads(file)
ofile = open("documents.txt", "w", encoding='utf-8');
for site in filejson:
	for post in site:
		ofile.write(post["link"] + "\t" + post["date"].replace("\n", "") + "\t")
		body = post["body"].replace("\t", " ")
		body = re.sub(r'(\r?\n)', ' ', body)
		body = re.sub(r'(\s)+', ' ', body)
		bodylen = len(body);
		if bodylen > 300:
			body = body[:297]
			body += "..."
		elif bodylen < 2:
			body = "(this post contains no text)";
		ofile.write(body + "\n")
		docnum+=1;
ofile.close();
print("{} {} {}".format("total of", docnum, "documents processed"));
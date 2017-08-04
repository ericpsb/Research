import json
import re
from urllib.parse import urlparse
docnum = 0
reject = 0
numsite = 0
with open("merged_file.json", "r", encoding='utf-8') as ifile:
	file = ifile.read()
filejson = json.loads(file)
ofile = open("documents.txt", "w", encoding='utf-8')
sites = [ "ablogonthespectrum.blogspot.com", "adiaryofamom.com", "adventuresinautism.blogspot.co.uk", "alyric.blogspot.com", "autism.typepad.com", "autisminnb.blogspot.com", "autismjabberwocky.blogspot.com", "autismnaturalvariation.blogspot.com", "autismschmatism.blogspot.com", "autismsedges.blogspot.com", "carrielink.blogspot.com", "club166.blogspot.com", "daysixtyseven.blogspot.com", "elvis-sightings.blogspot.com", "fullspectrummama.blogspot.com", "hoopdeedoo.blogspot.com", "injectingsense.blogspot.com", "joeyandymom.blogspot.com", "leftbrainrightbrain.co.uk", "letitbeautism.blogspot.com", "momnos.blogspot.com", "motherofshrek.blogspot.com", "onedadsopinion.blogspot.com", "roostercalls.blogspot.com", "spectrumliving.blogspot.com", "embracingchaos.stephanieallencrist.com", "stimcity.org", "susanetlinger.typepad.com", "susansenator.com", "teenautism.com", "theadventuresofboywonder.blogspot.com", "thefamilyvoyage.blogspot.com", "thismom.blogs.com", "confessionsofanaspergersmom.blogspot.com", "www.esteeklar.com", "www.jennyalice.com", "www.squashedmom.com", "www.squidalicious.com", "www.stimeyland.com", "autismandoughtisms.wordpress.com", "maternalinstincts.wordpress.com", "rebekahscot.wordpress.com", "rhemashope.wordpress.com", "specialed.wordpress.com", "therocchronicles.wordpress.com", "trydefyinggravity.wordpress.com" ]
resultjson = []
for site in filejson:
	numsite += 1
	rejected = reject
	for post in site:
		ofile.write(post["link"] + "\t")
		domain = '{uri.netloc}'.format(uri=urlparse(post["link"]))
		try:
			sites.index(domain)
		except ValueError:
			reject += 1
			break
		date = post["date"].replace("\n", "")
		date = re.sub(r'^\s*', "", date)
		ofile.write(date + "\t")
		body = post["body"].replace("\t", " ")
		body = re.sub(r'(\r?\n)', ' ', body)
		body = re.sub(r'(\s)+', ' ', body)
		bodylen = len(body);
		if bodylen > 300:
			body = body[:297]
			body += "..."
		elif bodylen < 2:
			body = "(this post contains no text)"
		ofile.write(body + "\n")
		docnum+=1;
	if rejected == reject:
		resultjson += site
ofile.close()
with open("filtered_merged_file.json", "w", encoding='utf-8') as ofile2:
	json.dump(resultjson, ofile2)
print("{} {} {} {} {} {} {}".format("total of", docnum, "documents from", numsite-reject, "sites included, rejected", reject, "sites"))
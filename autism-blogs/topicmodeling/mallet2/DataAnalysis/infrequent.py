# -*- coding: utf8 -*-
#Use to determine words that only appear in one specific blog
import json
import unicodedata
import nltk
from nltk.tokenize import RegexpTokenizer
import re



class Blog():
	def __init__(self, id, name):
		self.id = id
		self.name = name 
		self.postlist = []

class Post():
	def __init__(self, id, total, unique):
		self.blogid = id
		self.total = total
		self.unique = unique

def infrequent():
	blogs = ['ablogonthespectrum.blogspot.com', 'adiaryofamom.com', 'adventuresinautism.blogspot.co.uk', 'alyric.blogspot.com', 'aspergersquare8.blogspot.com', 'autism-vicky.blogspot.com', 'autism.typepad.com', 'autismandoughtisms.wordpress.com', 'autismblogsdirectory.blogspot.com', 'autismcrisis.blogspot.com:', 'autismgadfly.blogspot.com', 'autisminnb.blogspot.com', 'autismjabberwocky.blogspot.com', 'autismnaturalvariation.blogspot.com', 'autismschmatism.blogspot.com', 'autismsucksrocks.blogspot.com', 'bloom-parentingkidswithdisabilities.blogspot.com', 'carrielink.blogspot.com', 'chavisory.wordpress.com', 'club166.blogspot.com', 'confessionsofanaspergersmom.blogspot.com', 'daysixtyseven.blogspot.com', 'donnathomson.com', 'elvis-sightings.blogspot.com:', 'embracingchaos.stephanieallencrist.com', 'esteeklar.com', 'extraordinary-ordinary.net', 'fullspectrummama.blogspot.com', 'hoopdeedoo.blogspot.com', 'idoinautismland.com', 'injectingsense.blogspot.com', 'jennyalice.com', 'joeyandymom.blogspot.com', 'juststimming.wordpress.com', 'leftbrainrightbrain.co.uk', 'letitbeautism.blogspot.com', 'lizditz.typepad.com', 'lovethatmax.com', 'maternalinstincts.wordpress.com', 'mfamama.typepad.com:my-blog', 'momnos.blogspot.com', 'motherofshrek.blogspot.com', 'noahsdad.com', 'onedadsopinion.blogspot.com', 'questioning-answers.blogspot.com', 'qw88nb88.wordpress.com', 'rebekahscot.wordpress.com', 'rhemashope.wordpress.com', 'roostercalls.blogspot.com', 'specialed.wordpress.com', 'spectrumliving.blogspot.com', 'squashedmom.com', 'squidalicious.com', 'stimcity.org', 'stimeyland.com', 'susanetlinger.typepad.com', 'susansenator.com:blog', 'teenautism.com', 'theadventuresofboywonder.blogspot.com', 'thefamilyvoyage.blogspot.com', 'therocchronicles.wordpress.com', 'tinygracenotes.blogspot.com', 'trydefyinggravity.wordpress.com:tag:autism', 'unstrangemind.wordpress.com']
	result = {} #accumulator dictionary
	extra_data = []
	f = "../merged_file.json"
	with open(f, "rb") as infile:
    		jlist = (json.load(infile))
	count = 0
	blog_num = 1
	for blog in jlist:
		print "\n At blog" + str(blog_num) + "\n"
		currentblog = Blog(blog_num, blogs[blog_num-1])
		for post in blog:
			text = post["body"]
			text = text.lower()
			reg = re.compile('[^\W\d_][^\d\s]+[^\W\d_]', re.U)
			tokenizer = RegexpTokenizer(reg)
			total = 0
			unique = 0 
			for word in tokenizer.tokenize(text):
				try:
					if blog_num not in result[word]:
						result[word][blog_num] =1
						unique+=1
					else:
						result[word][blog_num] += 1

				except:
					result[word] = {blog_num:1}
					unique +=1
				total += 1
			currentpost = Post(blog_num, total, unique)
			currentblog.postlist.append(currentpost)

		blog_num += 1
		extra_data.append(currentblog)

	final_words = {}
	for word, blogs in result.items():
    		max_appear = 0
    		second_max = 0
    		total_appear = 0
    		for k,v in blogs.items():
    			if v >= max_appear:
    				second_max = max_appear
    				max_appear = v
    			total_appear += v
    		if total_appear > 100:
        		    final_words[word] = total_appear
	#f = open('workfile.txt', 'r+')
	#fb = open ('work.txt', 'r+')
	for word, number in final_words.items():
		#f.write(word + '\n')
		print str(number) + " " + word
	#maxpost = 0
	for blog in extra_data:
		uniquewords = 0
		totalwords = 0
		#fb.write(str(blog.id) + " " + str(len(blog.postlist)) + "\n")
		for post in blog.postlist:
			uniquewords += post.unique
			totalwords += post.total
			#f.write(str(post.total) +"\n")

		comma = ' '
		length = len(blog.postlist)
		uwordsperpost = float(uniquewords)/float(length)
		twordsperpost = float(totalwords)/float(length)
		#print str(blog.id) + comma + blog.name + comma + str(length) + comma + str(uniquewords) + comma + str(uwordsperpost) + comma + str(totalwords) + comma + str(twordsperpost)

	#print len(result)

if __name__ == '__main__':
	infrequent()

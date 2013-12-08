#Different Feature Extractors
#@Author: Crystal Qin
from __future__ import division
import nltk, MySQLdb,jsonrpclib
import sys, re,random,os,time,string
from pprint import pprint
import csv
from nltk.stem.wordnet import WordNetLemmatizer
import math
#from nltk.util import Deprecated
import nltk.classify.util # for accuracy & log_likelihood
from nltk.util import LazyMap
from corenlp import StanfordCoreNLP
from json import loads
from itertools import chain
from corenlp import batch_parse
from bisect import bisect_left, bisect_right
from nltk.corpus import stopwords

#experiment with stop words and puncts
#python corenlp/corenlp.py -H localhost -p 3455 -S stanford-corenlp-full-2013-06-20/
#python corenlp/corenlp.py -S stanford-corenlp-full-2013-06-20/
#python corenlp/fextractor.py
# cd /cygdrive/c/users/qin/cs_projects/tortoise/Research/corenlp-python
# training with 20, 30 and 50 randomly selected dataset
# using annotation randomly to test. 
# other classifiers decision trees 
# logistical regression
# googling around
listspath='lists/'
class FeatureExtractor(object):
    
    
    def __init__(self):
        self.texts={}
        self.collection=None
        self.stemmer = nltk.PorterStemmer()#choice of stemmer
        self.lemmer = WordNetLemmatizer()
        self.dlow_mid_cutoff= 3.48
        self.dmid_high_cutoff=6.10
        self.dsp_dict={}
        self.server = jsonrpclib.Server("http://127.0.0.1:8080")
        self.doc_sets={}
        
        #doc specific
        self.docID=0
        self.title_words=[]
        self.coreParsed=[]#the sentences(containing all its information) of this text
        self.offsets=[]
        #for all anotations of this doc
        self.start_indices=[]
        self.end_indices=[]
    
        
    def prepareExtractor(self):
        print 'execute extractor'
        self.preprocessDescriptiveness()
        #extract sets
        lstfiles=["subjective","report_verb","implicative","hedge","factive","bias-lexicon","assertive","negative-word", "positive-word"]
        for known_lst in lstfiles:
            self.doc_sets[known_lst]=set([self.preprocessEachWord(line.strip()) for line in open(listspath+known_lst+".txt", 'r')])
          
        #Train Model
        self.corpusFromDB()
        
    def executeExtractor(self):
        featuresets=self.train_model()
        print "Got train_set, start training models"
        #dt_classifier = nltk.DecisionTreeClassifier.train(train_set)
        random.seed(123456)
        random.shuffle(featuresets)
        size = int(len(featuresets) * 0.1)
        train_set, test_set = featuresets[size:], featuresets[:size]

        # Train up a classifier.

        nb_classifier = nltk.NaiveBayesClassifier.train(train_set)
        nb_classifier.show_most_informative_features(100)
        acc=nltk.classify.accuracy(nb_classifier, test_set)
        print "accuracy is: %f"%acc



    # For classifiers that can find probabilities, show the log
    # likelihood and some sample probability distributions.
        try:
            test_featuresets = [f for (f,l) in test_set]
            pdists = nb_classifier.batch_prob_classify(test_featuresets)
            ll = [pdist.logprob(gold)
                  for ((f, gold), pdist) in zip(test_set, pdists)]
            print('Avg. log likelihood: %6.4f' % (sum(ll)/len(test_set)))
            print()
            print('Unseen Names      P(Male)  P(Female)\n'+'-'*40)
            for ((name, gender), pdist) in list(zip(test_set, pdists))[:5]:
                if gender == 'True':
                    fmt = '  %-15s *%6.4f   %6.4f'
                else:
                    fmt = '  %-15s  %6.4f  *%6.4f'
                print(fmt % (name, pdist.prob('True'), pdist.prob('False')))
        except NotImplementedError:
             pass

        #dt_classifier = nltk.DecisionTreeClassifier.train(train_set)
        #dt_classifier.pp()
        #return dt_classifier
 
    
    
    # whether the words -2, -1, 0, 1, 2 is in the list

    def whetherInList(self, lst, index, words):
    #sents=nltk.sent_tokenize(filestream.read().lower())
        result=[False for i in range(5)]#0 false 1 true
    
        
        if (index > 1 and words[index-2] in lst):
                result[0]=True
        if(index > 0 and words[index-1] in lst):
                result[1]=True
        if (words[index] in lst):
                result[2]=True
           
        if(index < len(words)-1 and words[index+1] in lst):
                result[3]=True
            
        if(index < len(words)-2 and words[index+2] in lst):
                result[4]=True
        #print "word: %s %d"%(words[index], result[2])
        return result

    def preprocessDescriptiveness(self):
   
        dfile  = open(listspath+"ImageryRatings.csv", "rb")
        reader = csv.reader(dfile)
        next(reader, None)
    
        for row in reader:
        # Save header row.
            word=self.stemmer.stem((row[0].lower()))
            count=row[1]
            category="mid" 
            if(count < self.dlow_mid_cutoff):
                category='low'
            elif(count > self.dmid_high_cutoff):
                category="high"
            self.dsp_dict[word]=category
                
    def corpusFromDir(self):
        path = "../../../FA13/NLP/codes/data/"

    # Iterate through the  directory and build the collection of texts for NLTK.
        listing = os.listdir(path)
        for infile in listing:
            if infile.startswith('.'): #Mac directories ALWAYS have a .DS_Store file.
                continue               #This ignores it and other hidden files.
            url = path + infile
            f = open(url);
            raw = f.read()
            f.close()
            text = nltk.Text([self.preprocessEachWord(w) for w in nltk.word_tokenize(doc) if len(w) >= 1])
            self.texts.append(text)

    #Load the list of texts into a TextCollection object.
        return nltk.TextCollection(self.texts)
    
    def corpusFromDB(self):
        db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation')
        c=db.cursor()
        c.execute("SELECT  DISTINCT(doc_id),doc_html FROM Documents natural join Annotations WHERE doc_id != 1")#a_id > 125")
        
        rowall=c.fetchall()
        for row in rowall:
          
            doc=nltk.clean_html(row[1])
            text=nltk.Text([self.preprocessEachWord(w) for w in nltk.word_tokenize(doc) if len(w) >= 1])
            self.texts[int(row[0])]=text
        self.collection=nltk.TextCollection(self.texts.values())
        
    

# Function to create a TF*IDF vector for one document.  For each of
# our unique words, we have a feature which is the td*idf for that word
# in the current document
    def TFIDF(self, word,document):
        return self.collection.tf_idf(word,document)
   #extract for each article

    def extractDependency(self,text):
        print "dependency extraction"
        
        sents=nltk.sent_tokenize(text)
        
        currTotal=0

        for sent in sents:
            result=self.server.parse(sent)
            #pprint(result)
            newlsts=(loads(result))['sentences']
            if self.coreParsed == []:
                self.coreParsed=newlsts
            else:
                self.coreParsed.extend(newlsts)
            #pprint(newlsts)
            sent_len=int(newlsts[-1]['words'][-1][1]['CharacterOffsetEnd'])

            self.offsets.extend([currTotal for k in range(len(newlsts))])

            pprint(newlsts)
            currTotal+=sent_len
            assert(sent_len==len(sent)),('parsed_leng %d != expected %d '%(sent_len, len(sent)))
        
        
    def extractDependencyLarge(self):
        corenlp_dir = "stanford-corenlp-full-2013-06-20/"   
        raw_text_directory = "temp_raw_text/"
        parsed = batch_parse(raw_text_directory, corenlp_dir) 
        self.coreParsed=parsed.next()['sentences']
        print 'done\n'
        #pprint (self.coreParsed)
 
        
    def preprocessEachWord(self, word):
        return self.stemmer.stem(word.lower())    
       
   
    # %d is the word itself's location in -2, -1, 0, 1, 2 (or for bigram 0, 1)  
    #feature for a word      
    def generateFeatures(self, index, words):
        global dsp_dict
        fnames=["word", "word_bigram:%d", "word_trigram %d:", "pos_unigram:", "pos_bigram %d", "pos_trigram %d","sentence contains quotes:", "sentence length:", 'descriptiveness:%d', 'isInTitle:%d', 'TFIDF:']
        features={}
        text=['^']
        poses=['BEG']
        for wls in words:
            text.append(self.preprocessEachWord(wls[0]))
            poses.append(wls[1]['PartOfSpeech'])
        text.append("^")
        poses.append('END')
        #stemmed_words=[self.stemmer.stem(self.lemmer.lemmatize(w[])) for w in words] # stem or not?
        
        
        index+=1 #start from 0
        
        features[fnames[0]]=text[index]
        features[fnames[3]]=poses[index]
        
        
        features[fnames[1]%(0)]=(' '.join(text[index-1:index+1]))
        
        features[fnames[1]%(1)]=(' '.join(text[index:index+2]))
        features[fnames[4]%(0)]=(' '.join(poses[index-1:index+1]))
        features[fnames[4]%(1)]=(' '.join(poses[index:index+2]))
            
        features[fnames[2]%(0)]=(' '.join(text[index-1: index+2]))
        features[fnames[5]%(0)]=(' '.join(poses[index-1: index+2]))
        
        if(index>1):
            features[fnames[2]%(1)]=(' '.join(text[index-2: index+1]))
            features[fnames[5]%(1)]=(' '.join(poses[index-2: index+1]))
        else:
            features[fnames[2]%(1)]='null'
            features[fnames[5]%(1)]='null'
        
        if(index<len(poses)-2):
            features[fnames[2]%(-1)]=(' '.join(text[index: index+3]))
            features[fnames[5]%(-1)]=(' '.join(poses[index: index+3]))
        else:
            features[fnames[2]%(-1)]="null"
            features[fnames[5]%(-1)]="null"
        
        features[fnames[6]]=('\"' in text or '\'' in text)
        
       
            
        features[fnames[7]]=len(words)
        
        for i in range(-2, 3):
            #print text[index+i] 
            if (index+i) >0 and (index+i) < len(text) and text[index+i] in self.dsp_dict :
                features[fnames[8]%i]= self.dsp_dict[text[index+i]]
                features[fnames[9]%i]=text[index+i] in self.title_words
            else:
                features[fnames[8]%i]='null'
                features[fnames[9]%i]=False
        features[fnames[10]]=self.TFIDF(text[index],self.texts[self.docID])  
        
        # all the lists
        #lstfiles=["subjective","report_verb","implicative","hedge","factive","bias-lexicon","assertive","negative-word", "positive-word"]
        for known_set in self.doc_sets.keys():
	        #print "%s in %s is %d"%(text[index], known_set, text[index] in self.doc_sets[known_set])
            features[("is "+known_set+" %d:")%(0)]=(text[index] in self.doc_sets[known_set]) 
            #lst=[self.preprocessEachWord(line.strip()) for line in open(listspath+known_lst+".txt", 'r')]
            #rls=self.whetherInList(lst, index, text)
            #for i in range(len(rls)):
                #features[("is "+known_lst+" %d:")%(i-2)]=rls[i] 
        return features
    
            
 #cstart: the offset of the first char in the word, cend: the offset of the last char in the word       
    def isHighlighted(self,cstart,cend, i):
        start_pos=bisect_right(self.start_indices[i], cstart)-1 #right most that is <= cstart
        end_pos=bisect_left(self.end_indices[i], cend) # left most that is >= cend
        #print 'check if heighlighted: %d %d\n'%(cstart, cend)
        #print 'len of start indices %d' start_pos%()
        if start_pos > 0:
            end_val=self.end_indices[i][start_pos]
            if cstart <= end_val:
                print '%d %d %d %d\n'%(self.start_indices[i][start_pos], end_val, cstart, cend)
                return 'True'
        if end_pos < len(self.end_indices[i]):
            start_val=self.start_indices[i][end_pos]
            #assert(end_pos < len(self.start_indices[i])),('end_pos %d endi size %d, starti size %d, ')
            if start_val <= cend:
                print '%d %d %d %d\n'%(start_val, self.end_indices[i][end_pos], cstart, cend)
                return 'True'
        
        #for start, end in self.indices:
         #   if start <=cstart <=end or start <= cend <= end:
          #      print '%d %d %d %d\n'%(start, end, cstart, cend)
           #     return True
        return 'False'
        
                
            
    def train_model(self):
        
       
        train_set=[]
        puncts='#$&\()*+,-./:;<=>@[\\]^_`{|}~'
        for doc_id in self.texts.keys():
            print "Start Processing document: %d"%doc_id
            self.docID=doc_id
            self.offsets=[]
            self.coreParsed=[]
            
            db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation', charset='ascii')
            c=db.cursor()
            #c.execute('set charset utf8')
           
            c.execute("SELECT doc_html from Documents WHERE doc_id = %s"%(doc_id,))
           
            text=nltk.clean_html(c.fetchone()[0])
            separate=text.split('\n',1)
            self.title_words=[self.stemmer.stem(self.lemmer.lemmatize(w)) for w in nltk.word_tokenize(separate[0])]
            
            self.extractDependency(text)
            
            c.execute('SELECT char_annotation from Annotations WHERE doc_id = %s'%(doc_id,))
            rows=c.fetchall()

            num_ann=len(rows)
            self.start_indices=[]
            self.end_indices=[]

            for i in range(num_ann):
                indexStr=rows[i][0]
                if indexStr is None:
                    continue
                self.start_indices.append([])
                self.end_indices.append([])
                isents=indexStr.split('.')
                del isents[-1]
                for sentInd in isents:
                    il=sentInd.split(" ")
                    self.start_indices[i].append(int(il[0])) #title??
                    self.end_indices[i].append(int(il[1]))
                #pprint (self.coreParsed[0])
            pprint(self.start_indices)
            pprint(self.end_indices)
            for i in range(len(self.coreParsed)):
                    #sent=self.coreParsed[i]['text']
                tuples=self.coreParsed[i]['dependencies']
                    #pprint(tuples)
                words=self.coreParsed[i]['words'] #words are words properties
                for windex in range(len(words)):
                    
                    #ignore punctuations
                    if words[windex][0] in puncts:
                        continue
                    f1=self.generateFeatures(windex,words)
                    for [rel, gov, sub] in tuples:
                        thew=words[windex][0]
                            
                        if thew == gov:
                            f1["dependency: %s %s"%(rel, 'gov')]=True
                        elif thew == sub:
                            f1["dependency: %s %s"%(rel,'sub')]=True
                            #else:
                                #f1["dependency: %s %s"%(rel,'sub')]=False
                                #f1["dependency: %s %s"%(rel, 'gov')]=False
                        for a in range(len(self.start_indices)):
                            train_set.append((f1, self.isHighlighted(int(words[windex][1]['CharacterOffsetBegin'])+self.offsets[i],int(words[windex][1]['CharacterOffsetEnd'])+self.offsets[i],a)))
            

        return train_set
        
                            
        
def main(argv=None):
    print "Start Feature Extractor"
    # Preprocess read file
    
    
    #execute
    extractor=FeatureExtractor()
    extractor.prepareExtractor()
    #time.sleep(300)
    classifier=extractor.executeExtractor()
    #context=nltk.word_tokenize("C is brave enough to handle that ?? tonde mo nai")
    #print classifier.classify(self.generateFeatures(0, context,['aggressive']))

        #[[randint(0, len(re.findall(r'\w+', sent))),randint(0, len(re.findall(r'\w+', sent)))] for sent in sents]  
    
        
    
    
if __name__ == "__main__":
    main() 

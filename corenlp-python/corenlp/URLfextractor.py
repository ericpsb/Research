#!/usr/bin/env python
from __future__ import division
from boilerpipe.extract import Extractor
import nltk, MySQLdb,jsonrpclib
import sys, re,random,os,time,string, unicodedata
from pprint import pprint
import csv, collections
from json import loads
from corenlp import batch_parse
from bisect import bisect_left, bisect_right
import pickle, cPickle
import copy


#nltk imports
from nltk.stem.wordnet import WordNetLemmatizer
import nltk.classify.util # for accuracy & log_likelihood
import nltk.metrics
#from corenlp import StanfordCoreNLP

from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.utils.extmath import density
from sklearn import metrics
from sklearn.feature_extraction import DictVectorizer,FeatureHasher
from sklearn.naive_bayes import GaussianNB
from sklearn.dummy import DummyClassifier
import numpy as np
import scipy as sp
from scipy.sparse import vstack
from sklearn import cross_validation
from sklearn import svm
from sklearn.externals import joblib
listspath='lists/'


# set of booleans to turn on or off certain features
feat_words = True # use the token- and lemma-based features
feat_POS = True # use the POS-based features
feat_entity = True # use the named entity type as a feature
feat_relns = True # use grammatical dependencies as a feature
feat_sent_len = True # use the sentence length feature
feat_title = True # use whether the word is in the title as a feature
feat_TFIDF = True # use TFIDF as a feature
feat_imagery = True # use the imagery/descriptiveness rating feature
feat_word_lists = True # use the special lists of words (factives, implicatives, etc.)



class URLFeatureExtractor(object):
    
    def __init__(self):
        self.texts={}
        self.collection=None
        self.stemmer = nltk.PorterStemmer()#choice of stemmer
        self.lemmer = WordNetLemmatizer()
        self.dlow_mid_cutoff= 3.48
        self.dmid_high_cutoff=6.10
        self.dsp_dict={}
        self.server = jsonrpclib.Server("http://127.0.0.1:5000")
        self.doc_sets={}
        self.tfidf_bins = {}
        self.offsets=[]
    
    def prepareExtractor(self, URL, doc_num):
        """
        Prepare feature extractor by preprocessing and storing the lists we are going to use and loading corpus from DB.
        @param doc_num: the total number of documents you want to include in this training and testing
        """
        print 'Execute extractor'
        self.preprocessDescriptiveness()
        
        lstfiles=["subjective","report_verb","implicative","hedge","factive","entailment","bias-lexicon","assertive","negative-word", "positive-word"]
        for known_lst in lstfiles:
            # epsb: changing to use dict rather than set
            self.doc_sets[known_lst] = dict( [(self.preprocessEachWord(line.strip()), True) 
                    for line in open(listspath+known_lst+".txt", 'r')] )
            #self.doc_sets[known_lst]=set([self.preprocessEachWord(line.strip()) for line in open(listspath+known_lst+".txt", 'r')])
        self.extract_text_and_html(URL)
        #build corpus
        self.addTOcorpusFromDB(doc_num)
    
    def executeExtractor(self):
        feat=self.generate_feature_lists(doc_num)
        vec=FeatureHasher(non_negative=True)
        self.featureData=vec.transform(feat)
        
    
    def predictions(self,classifier, feat, doc_num):
        clf=loadModel(classifier)
        #g=open("hasher.pickle")
        #vec = pickle.load(g)
        #g.close()
        print "Predicting..."
        #print featureData
        self.preds=clf.predict(self.featureData)
        self.predProbs=clf.predict_proba(self.featureData)
        self.lenientPred=[]
        self.results=[]
        self.probResults=[]
        for p,f in enumerate(feat):
            #self.results.append([f['lemma'],preds[p]])
            #self.probResults.append([f['lemma'],predProbs[p][1]])
            if self.predProbs[p][1]>=0.33:
                self.lenientPred.append(1)
            else:
                self.lenientPred.append(0)
        
    
    def runEnsemble(self,classes):
        preds=[]
        allF=0
        test_time=0
        train_time=0
        count=1;
        #g=open("hasher.pickle")
        #vec = pickle.load(g)
        #g.close()
        
       
        for name in classes:
           
            clf=loadModel(name)
            #clf.fit(self.X_train, self.y_train)
           
            #pred=clf.predict(self.X_test)
            try:
                predp = clf.predict_proba(self.featureData)
                predp=[i[1] for i in predp]
                #print predp
            except:
                d = clf.decision_function(self.featureData)
                predp= np.exp(d) / (1 + np.exp(d))
                #predp=1/(1 + np.exp(-d))
                #print predp
            #f1_s = metrics.f1_score(self.y_test, pred, pos_label=1, average='weighted')
            #acc=metrics.accuracy_score(self.y_test,pred)
            #allF+=f1_s*acc
            #pred=[np.power(i,1/2)*f1_s*acc for i in predp]
            
            #print pred
            if count<=1:
                preds=predp
            else:
                preds=[preds[i]+predp[i] for i in range(len(predp))]
            #print preds
            count +=1
        #print preds
        
        #predicts=[1 if i/allF>=float(1/3.0) else 0 for i in preds]
        #predicts=[1 if i>=1 else 0 for i in preds]
        numC=len(classes)
        self.predicts=[1 if i/numC>=float(1/2.0) else 0 for i in preds]
	   
    
     

    def extract_text_and_html(self,URL):
        #check if nytimes
        if string.find(URL,'www.nytimes.com')!=-1:
            #double redirect before boilerpipe extraction
            self.get_NYTimesArticle_Text_and_Html(URL)
        else:
            try:
                #regular boilerpipe extraction
                self.get_Article_Text_and_Html(URL)
            except:
                #single redirect before boilerpipe extraction
                print 'special article'
                self.get_SpecialArticle_Text_and_HTMl(URL)
        
        
    def preprocessDescriptiveness(self):
   	"""
	Preprocess Decriptiveness list for later use
	"""
        dfile  = open(listspath+"ImageryRatings.csv", "rb")
        reader = csv.reader(dfile)
        next(reader, None)
    
        for row in reader:
        # Save header row.
            word=self.stemmer.stem((row[0].lower()))
            count=row[1]
            category=0.66  #"mid"
            if(count < self.dlow_mid_cutoff):
                category=0.33 #'low'
            elif(count > self.dmid_high_cutoff):
                category=1 #"high"
            self.dsp_dict[word]=category
        
    
    def addTOcorpusFromDB(self,doc_num):
        """
        Build corpus from data in DB
        @param doc_num: the number of docs you are gonna use
        """

        try:
            f = open('texts.pickle')
            self.texts=pickle.load(f)
            f.close()
        except:
            db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation')
            c=db.cursor()
            ## we only want documents that have at least three valid annotations
            c.execute("SELECT  doc_id, doc_html, sum(valid) as tot_valid FROM Documents natural join Annotations WHERE doc_id > 1 group by doc_id having tot_valid >= 3 order by doc_id desc LIMIT %s "%(doc_num,))#a_id > 125")
            ##c.execute("select doc_id, doc_html from Documents where doc_id > 1 order by doc_id desc LIMIT %s"%(doc_num,))
            #
            rowall=c.fetchall()
            rowsTaken=[]
            for row in rowall:
                doc=nltk.clean_html(row[1])
                texty=nltk.Text([self.preprocessEachWord(w) for w in nltk.wordpunct_tokenize(doc) if len(w) >= 1 and not all(a in string.punctuation for a in w)])
                self.texts[int(row[0])]=texty
                rowsTaken.append(row[0])
       
        newText=nltk.Text([self.preprocessEachWord(w) for w in nltk.wordpunct_tokenize(self.extracted_text) if len(w) >= 1 and not all(a in string.punctuation for a in w)])
        self.texts[0]=newText
        self.rowNum=0
        self.collection=nltk.TextCollection(self.texts.values())
        
    
    def TFIDF(self, word,document):
	"""
	Calculate the tf_idf bin of a WORD in a certain DOCUMENT in our corpus
        @param: the target word
        @param: the target document
	"""
        if document not in self.tfidf_bins:
            self.tfidf_bins[document] = {}
            # get the tfidf scores for all tokens in this document
            token_freq = [(self.collection.tf_idf(w, document), self.collection.tf(w,document), 
                    self.collection.idf(w, document), w) for w in document.vocab().samples() if 
                    not all(a in string.punctuation for a in w)]
            token_freq.sort(reverse=True)
            
            # based on the tfidf scores, assign words into bins
            interval = len(token_freq) / 36 # make 8 bins of increasing size
            cur_bin = 1
            cur_cutoff = interval
            for tf in token_freq:
                token = tf[-1]
                if token_freq.index(tf) >= cur_cutoff:
                    cur_bin += 1
                    cur_cutoff += cur_bin * interval
                # cap the number of bins at 8; this addressing rounding issues causing more bins
                if cur_bin > 8:
                    cur_bin = 8
                self.tfidf_bins[document][token] = cur_bin
        # punct get the max tfidf bin
        # normalize to range (0,1)
        return (self.tfidf_bins[document].get(word, 8)) / 8.0
    
    
    def extract_sentence_info(self):
        """
        Extract information of a text using stanford corenlp
        @param text: the input text
        """
        sents=nltk.sent_tokenize(self.extracted_text)
        currTotal=0
        sent_index = 0
        self.coreParsed=[]
        for sent in sents:
            result=self.server.parse(sent)
            newlsts=(loads(result))['sentences']
            if  not self.coreParsed:
                self.coreParsed=newlsts
            else:
                self.coreParsed.extend(newlsts)
            #sent_len=int(newlsts[-1]['words'][-1][1]['CharacterOffsetEnd'])
            sent_len = \
                    int(self.coreParsed[sent_index]['words'][-1][1]['CharacterOffsetEnd'])
    
            self.offsets.extend([currTotal for k in 
                    range(len(self.coreParsed[sent_index]))])
    
            #pprint(newlsts)
            currTotal+=sent_len
            sent_index += 1
            #assert(sent_len==len(sent)),('parsed_leng %d != expected %d '%(sent_len, len(sent)))
    
    
     
    def preprocessEachWord(self, word):
        """
        Implement any preprocessing needed to be done for each word	
        """
        return self.stemmer.stem(word.lower())
    
      
    def generateFeatures(self, outer_index, words):
        """
        Generate feature vectors for words in a sentence.
        @param words: all the words in a sentence.
        @param outer_index: the word position in the sentence
        """
        features={}
        tokens = ['^^^']
        lemmas = ['^^^']
        stems=['^^^']
        entities=['^^^']
        for wls in words:
            #text.append(self.preprocessEachWord(wls[0]))
            tokens.append(wls[0].lower())
            lemmas.append(wls[1]['Lemma'])
            stems.append(self.preprocessEachWord(wls[0]))
            entities.append(wls[1]['NamedEntityTag'])
        tokens.append("^^^")
        lemmas.append("^^^")
        stems.append("^^^")
        entities.append('^^^')
        
        index = outer_index + 1 # adjust for initial and terminal strings
        
        fnames = [] # this is our list of feature names
        
        if feat_words:
            # use the token and lemma (and +/- 1,2) features
            
            fnames.extend(["token", "token: -1",  'token +1', "token: -2", 'token +2'])
            features['token ' + tokens[index]] = 1
            token=tokens[index]
            self.plus_minus_features_list('token', 1, tokens, index, features, True)
            self.plus_minus_features_list('token', 2, tokens, index, features, True)
        
            fnames.extend(['lemma', 'lemma: -1', 'lemma: +1', 'lemma: -2', 'lemma: +2'])
            features['lemma ' + lemmas[index]] = 1
            self.plus_minus_features_list('lemma ', 1, lemmas, index, features, True)
            self.plus_minus_features_list('lemma ', 2, lemmas, index, features, True)
                
            # bigrams
            fnames.extend(['bigram -1', 'bigram +1'])
            # ignore bigrams that include stopwords, punctuation, and numbers
            if index > 0:
                if not self.filter_word(lemmas[index-1]):
                    features['bigram -1 ' + lemmas[index-1] + ' ' + lemmas[index]] = 1
            if index < len(lemmas) - 1:
                if not self.filter_word(lemmas[index+1]):
                    features['bigram +1 ' + lemmas[index] + ' ' + lemmas[index+1]] = 1
            
            # trigrams
            fnames.extend(['trigram -1', 'trigram 0', 'trigram +1'])
            # ignore trigrams that include stopwords, punctuation, and numbers
            if index > 1:
                if not (self.filter_word(lemmas[index-2]) or self.filter_word(lemmas[index-1])):
                    features['trigram - 1 ' + lemmas[index - 2] + ' ' + lemmas[index - 1] \
                            + lemmas[index]] = 1
            if index > 0 and index < len(lemmas) - 1:
                if not (self.filter_word(lemmas[index-1]) or self.filter_word(lemmas[index+1])):
                    features['trigram 0 ' + lemmas[index - 1] + ' ' + lemmas[index] + ' ' + \
                            lemmas[index + 1]] = 1
            if index < len(lemmas) - 2:
                if self.filter_word(lemmas[index+1]) or self.filter_word(lemmas[index+2]):
                    features['trigram +1 ' + lemmas[index] + ' ' + lemmas[index + 1] + ' ' + \
                            lemmas[index + 2]] = 1
        
        if feat_POS:
            # use the POS, POS +/- 1, and POS +/- 2 features
            fnames.extend(["pos", "pos -1", 'pos +1',  "pos -2", 'pos +2'])
            
            poses=['BEG']
            for wls in words:
                poses.append(wls[1]['PartOfSpeech'])
            poses.append('END')
            
            features['pos' + poses[index]] = 1
            self.plus_minus_features_list('pos', 1, poses, index, features)
            self.plus_minus_features_list('pos', 2, poses, index, features)
        
        if feat_entity:
            # use the type of named entity as a feature
            fnames.extend(['entity type', 'entity bigram - 1', 'entity bigram + 1', 
                    'entity trigram - 1', 'entity trigram 0', 'entity trigram + 1'])
            features['entity type ' + entities[index]] = 1
            self.plus_minus_features_list('entity type', 1, entities, index, features)
            self.plus_minus_features_list('entity type', 2, entities, index, features)
            '''
            # performance drops a tiny bit for logistic regression when using entity n-grams
            # entity bigrams
            if index > 0:
                if self.filter_word(lemmas[index-1]):
                    features['entity bigram - 1'] = 'null'
                else:
                    features['entity bigram - 1'] = entities[index-1] + ' ' + entities[index]
            else:
                features['entity bigram - 1'] = 'null'
            if index < len(entities) - 1:
                if self.filter_word(lemmas[index+1]):
                    features['entity bigram + 1'] = 'null'
                else:
                    features['entity bigram + 1'] = entities[index] + ' ' + entities[index+1]
            else:
                features['entity bigram + 1'] = 'null'
            
            # entity trigrams
            if index > 1:
                if self.filter_word(lemmas[index-2]) or self.filter_word(lemmas[index-1]):
                    features['entity trigram - 1'] = 'null'
                else:
                    features['entity trigram - 1'] = entities[index-2] + ' ' + entities[index-1] +\
                            ' ' + entities[index]
            else:
                features['entity trigram - 1'] = 'null'
            if index > 0 and index < len(entities) - 1:
                if self.filter_word(lemmas[index-1]) or self.filter_word(lemmas[index+1]):
                    features['entity trigram 0'] = 'null'
                else:
                    features['entity trigram 0'] = entities[index-1] + ' ' + entities[index] +\
                            ' ' + entities[index+1]
            else:
                features['entity trigram 0'] = 'null'
            if index < len(entities) - 2:
                if self.filter_word(lemmas[index+1]) or self.filter_word(lemmas[index+2]):
                    features['entity trigram + 1'] = 'null'
                else:
                    features['entity trigram + 1'] = entities[index] + ' ' + entities[index+1] +\
                            ' ' + entities[index+2]
            else:
                features['entity trigram + 1'] = 'null'
            '''
        
        if feat_sent_len:
            # use the sentence length feature
            fnames.extend(['sentence length', 'sentence position'])
            features['sentence length']=len(words)
            sentence_position = float(index) / float(len(words))
            if sentence_position < (float(1/3.0)):
                features['sentence position:']=1
            elif sentence_position < (float(2/3.0)):
                features['sentence position:']=2
            else:
                features['sentence position:']=3
        
        if feat_title:
            # use whether the word is in the title as a feature
            fnames.extend(['InTitle'])
            features['InTitle'] = int(stems[index] in self.title_words)
        
        if feat_TFIDF:
            # use TFIDF as a feature
            fnames.extend(['TFIDF'])
            features['TFDIF']=self.TFIDF(stems[index],self.texts[self.rowNum])
        
        if feat_imagery:
            # use the imagery/descriptiveness rating feature
            fnames.extend(['descriptiveness', 'descriptiveness +1', 'descriptiveness -1', 
                    'descriptiveness +2', 'descriptiveness -2', 'descriptiveness average'])
            
            try:
                features['descriptiveness'] = self.dsp_dict[stems[index]]
            except KeyError:
                features['descriptiveness'] = 'null'
            self.plus_minus_features_dict('descriptiveness', 1, stems, self.dsp_dict, index, 
                    features)
            self.plus_minus_features_dict('descriptiveness', 2, stems, self.dsp_dict, index, 
                    features)
            
            desc_avg = 0
            desc_avg += (0 if features['descriptiveness'] == 'null' else 
                    features['descriptiveness'])
            desc_avg += (0 if features['descriptiveness: +1'] == 'null' else 
                    features['descriptiveness: +1'])
            desc_avg += (0 if features['descriptiveness: +2'] == 'null' else 
                    features['descriptiveness: +2'])
            desc_avg += (0 if features['descriptiveness: -1'] == 'null' else 
                    features['descriptiveness: -1'])
            desc_avg += (0 if features['descriptiveness: -2'] == 'null' else 
                    features['descriptiveness: -2'])
            desc_count = sum([features['descriptiveness'] != 'null', features['descriptiveness: +1'] != 'null', features['descriptiveness: +2'] != 'null', features['descriptiveness: -1'] != 'null', features['descriptiveness: -2'] != 'null'])
            if desc_count > 0:
                desc_avg /= desc_count
                features['descriptiveness average'] = desc_avg
            features.pop('descriptiveness')
            for i in range(1,3):
                features.pop("descriptiveness: -%d" % i)
                features.pop("descriptiveness: +%d" % i)
            
        
        if feat_word_lists:
            # use the special lists of words (factives, implicatives, etc.)
            for known_set in self.doc_sets.keys():
                fnames.append(known_set)
                
                features[(known_set)] = 1 if stems[index] in self.doc_sets[known_set] else 0
                self.plus_minus_features_dict(known_set, 1, stems, self.doc_sets[known_set],
                        index, features)
                self.plus_minus_features_dict(known_set, 2, stems, self.doc_sets[known_set],
                        index, features)
                features[known_set + " in context"] = 1 if (features[known_set + ": +1"]==1 or \
                        features[known_set + ": -1"]==1 or features[known_set + ": +2"]==1 or \
                        features[known_set + ": -2"]==1) else 0
                for i in range(1,3):
                    features.pop(known_set + ": -%d" % i)
                    features.pop(known_set + ": +%d" % i)
        return features,token
    
     
    
    def plus_minus_features_list(self, fname, offset, values_list, index, features, filter=False):
        '''
        Convenience method for features that involve words +/- some fixed index from the current 
        word index. Works when values for features are stored in a list.
        @param fname: The name of the feature.
        @param offset: How much to +/-.
        @param values_list: The list of values into which to index.
        @param index: Current index for checking the size of the offset.
        @param features: The feature vector to update.
        @param filter: Whether we should try to filter the values as possible words. Default: False.
        '''
        if index > 0:
            if filter:
                if not self.filter_word(values_list[index - offset]):
                    features[fname + ": -%d" % offset + values_list[index - offset]] = 1
            else:
                features[fname + ": -%d" % offset + values_list[index - offset]] = 1
            
        if index < len(values_list) - offset:
            if filter:
                if self.filter_word(values_list[index + offset]):
                    features[fname + ": +%d" % offset + values_list[index + offset]] = 1
            else:
                features[fname + ": +%d" % offset + values_list[index + offset]] = 1
    
    
    def plus_minus_features_dict(self, fname, offset, key_list, values_dict, index, features):
        '''
        Convenience method for features that involve words +/- some fixed index from the current 
        word index. Works when values for features are stored in a dictionary.
        @param fname: The name of the feature.
        @param offset: How much to +/-.
        @param key_list: The list of keys into which to index.
        @param values_dict: The dictionary of values; the key comes from key_list.
        @param index: Current index for checking the size of the offset.
        @param features: The feature vector to update.
        '''

        #if index > 0:
	try:
	    features[fname + ": -%d" % offset] = values_dict[key_list[index - offset]]
	except KeyError:
	    features[fname + ": -%d" % offset] = 'null'	
        #if index <= len(key_list) - offset:
	try:
	    features[fname + ": +%d" % offset] = values_dict[key_list[index + offset]]
	except :
	    features[fname + ": +%d" % offset] = 'null'


     
    def filter_word(self, word):
            """
            Return true if this words meets any of the criteria for filtering (stopword, punctuation,
            numeric, etc.).
            @param word: The word to be checked.
            @return: True if the word should be filtered out, False if the word should be included.
            """
            return (
                # stopwords
                #word in nltk.corpus.stopwords.words('english') or 
                # punctuation and numbers
                #all(a in string.punctuation or unicode.isnumeric(a) for a in word) # or
                # "words" that begin with punctuation
                #unicodedata.category(word[0])[0] == 'P' or 
                # "words" that begin with symbols
                #unicodedata.category(word[0])[0] == 'S' or 
                # "words" that begin with numbers
                #unicodedata.category(word[0])[0] == 'N' or 
                # short words
                #len(word) < 3
            )
    
  
   
    def generate_feature_lists(self,doc_num):
        features=[]
        self.tokens=[]
        separate=self.extracted_text.split('\n',1)
        print "Extracting features..."
        self.title_words=[self.stemmer.stem(self.lemmer.lemmatize(w)) for w in nltk.wordpunct_tokenize(separate[0])]
        print 'parsing...'
        self.extract_sentence_info()
        for i in range(len(self.coreParsed)):
                #sent=self.coreParsed[doc_id][i]['text']
            tuples=self.coreParsed[i]['dependencies']
                #pprint(tuples)
            words=self.coreParsed[i]['words'] #words are words properties
            for windex in range(len(words)):
                #ignore punctuations
                if self.filter_word(words[windex][0]):
                    continue 
        
                f1,t=self.generateFeatures(windex,words)
                if feat_relns:
                    for [rel, gov, sub] in tuples:
                        thew=words[windex][0]
        
                        if thew == gov:
                            f1["dependency: %s %s"%(rel, 'gov')]=1
                        elif thew == sub:
                            f1["dependency: %s %s"%(rel,'sub')]=1
                        #else:
                            #f1["dependency: %s %s"%(rel,'sub')]=False
                            #f1["dependency: %s %s"%(rel, 'gov')]=False
                        # also grab whether this word is the root of its sentence
                        if rel == 'root':
                            f1["ROOT"] = 1
                        else:
                            f1["ROOT"] = 0
                features.append(f1)
                self.tokens.append(t)
        return features


    
    def get_SpecialArticle_Text_and_HTMl(self, URL):
        start=str(URL.rsplit('.',1)[1])
        ext=start[0:string.find(start,'/')]
        print ext
        currLink = URL[string.find(URL, "//")+2:string.find(URL,str(ext))+len(ext)]
        offset = URL[string.find(URL,str(ext))+len(ext):len(URL)]
        c = httplib.HTTPConnection(currLink)
        c.request("HEAD",offset)
        r1 = c.getresponse()
        
        # get the string repsentation of the http response
        data = r1.read()
            
        for q in r1.getheaders():
            if q[0] == 'location':
                nextLoc = q[1]
                
                self.extracted_text,self.extracted_html=get_Article_Text_and_Html(nextLoc)
        
                    
    def get_NYTimesArticle_Text_and_Html(self, URL):
        #NYT
        
        cj = CookieJar()
        p = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)).open(URL)
        
        data=p.read()
        # get the post data from the link here
        begin='"<p class="story-body-text story-content"'
        extra=len(' data-para-count="214" data-total-count="214" itemprop="articleBody" id="')
        end='<footer class="story-footer'
        if string.find(data,str(end))==-1:
            end='</article>'
            
        if string.find(data,"&amp;") !=-1:
            data=string.replace(data,"&amp;","&")
        if string.find(data,"&quot;") !=-1:
            data=string.replace(data,"&quot;","\"")
            # check to see if this article is multiple pages
        
        
        if(string.find(data, '<div id="pageLinks">')!=-1):
            print 'MULTIPAGE'
                # loop over paragraphs in article - WARNING - the following code is specific for NYT
            article = data[string.find(data,'data-title')+12:string.find(data,'data-description')]
            beg='" id="story-continues-'
            #en='Continue reading the main story</a>'
            en='<a class="visually-hidden skip-to-text-link"'
            art=data[string.find(data,str(begin))+len(begin)+extra:string.find(data,str(end)),string.find(data,str(begin))+len(begin)+extra]
            while string.find(art, str(beg))!=-1 and string.find(art, str(en))!=-1:
                art= art[string.find(art, str(beg))+len(beg)+3:len(art)]
                if string.find(art, str(en))!=-1:
                    article = article + art[0:string.find(art, str(en))]
                    art=art[string.find(art, str(en)):len(art)]
            
            article = article + art[0:string.find(art, str(end))]
            
                    # retrieve the number of pages in the article and grab article from each one	
            page = data[string.find(data, '<div id="pageLinks">'):len(data)]
            page = page[0:string.find(page, '</div>')]
                    
                    # loop over the different pages 
            while(string.find(page, "MultiPagePageNum")!=-1):
                offset = page[string.find(page, 'href="')+6:len(page)]
                offset = offset[0:string.find(offset, '">')]
                            # form the next location and retrieve the html 
                nextLoc = "http://www.nytimes.com"+offset
                request = urllib2.Request(nextLoc)
                resp = urllib2.urlopen(nextLoc)
                data = resp.read()
                #print "urllib data: ", data
                        # loop over paragraphs in article for different pages- WARNING - the following code is specific for NYT
                
                art=data[string.find(data,str(begin))+len(begin)+extra:string.find(data,str(end))]
                while string.find(art, str(beg))!=-1 and string.find(art, str(en))!=-1:
                    art= art[string.find(art, str(beg))+len(beg)+3:len(art)]
                    if string.find(art, str(en))!=-1:
                        article = article + art[0:string.find(art, str(en))]
                        art=art[string.find(art, str(en)):len(art)]
            
                article = article + art[0:string.find(art, str(end))]
            
                #print "Article is: ", article
                page = page[string.find(page, "href=")+16:len(page)]
                    
                    # get the content
        
            conn0.close()
            conn1.close()
           
        
        else:
            # loop over paragraphs in article - WARNING - the following code is specific for NYT
            article = data[string.find(data,'data-title')+12:string.find(data,'data-description')-2]+"\n"
            
            beg='" id="story-continues-'
            #en='Continue reading the main story</a>'
            en='<a class="visually-hidden skip-to-text-link"'
            art=data[string.find(data,str(begin))+len(begin)+extra:string.find(data,str(end))+len(end)]
            while string.find(art, str(beg))!=-1 and string.find(art, str(en))!=-1:
                
                art= art[string.find(art, str(beg))+len(beg)+3:len(art)]
                if string.find(art, str(en))!=-1:
                    article = article + art[0:string.find(art, str(en))]
                    art=art[string.find(art, str(en))+ len(en):len(art)]
            
            article = article + art[0:string.find(art, str(end))]
            
          
        while string.find(article,'</figure>')!=-1:
            try:
                article=article[0:string.find(article,'<figure')] + article[string.find(article,'</figure>')+9:len(article)]
            except:
                article=article 
    
        article=nltk.clean_html(article)
        self.extracted_text=article
        self.extracted_html=data
                
                
    def get_Article_Text_and_Html(self, URL):
        "extract unicode text and html from given URL"
        extractor = Extractor(extractor='ArticleExtractor', url=URL)
        self.extracted_text = extractor.getText()
        self.extracted_html = extractor.getHTML()
        
def loadModel(type):
    """
    load the saved model
    @param type: the type of the classifier you are loading
    """
    f = 'classifiers/'+type+'_classifier.pickle'
    model=joblib.load(f,mmap_mode='c')
    #f.close()
    return model    
 
URL1="http://articles.chicagotribune.com/2008-09-27/news/0809260511_1_blagojevich-administration-lucio-guerrero-blagojevich-spokesman"
URL2="http://www.huffingtonpost.com/rj-eskow/obama-could-appoint-a-peo_b_5452814.html?utm_hp_ref=politics"
URL3="http://www.dailykos.com/story/2014/06/17/1307586/-Guess-who-this-North-Carolina-Republican-means-by-the-traditional-population"
URL4="http://www.cnsnews.com/news/article/ali-meyer/price-index-meats-poultry-fish-eggs-rockets-all-time-high"
URL5="http://www.politico.com/story/2014/06/clinton-library-memos-kyoto-protocol-china-india-107545.html"
Articles=[URL1, URL2, URL3, URL4, URL5]
classifier='Logistic Classifier'
doc_num='76'
artsINFO=[]

classes= [
            "SGD with l2 penalty hinge 50",
            "SGD with l1 penalty hinge 50",
            "SGD with l2 penalty hinge 25",
            "SGD with l1 penalty hinge 25",
            "SGD with l2 penalty hinge 20",
            "SGD with l1 penalty hinge 20",
            "SGD with l1 penalty log 20",
            "SGD with l2 penalty log 20",
            "SGD with l1 penalty log 25",
            "SGD with l2 penalty log 25",
            "SGD with l1 penalty log 50",
            "SGD with l2 penalty log 50",
            #"SGD with l1 penalty huber 20",
            #"SGD with l2 penalty huber 20",
            "SGD with l1 penalty huber 25",
            #"SGD with l2 penalty huber 25",
            #"SGD with l1 penalty huber 50",
            #"SGD with l2 penalty huber 50",
            #"Perceptron 42",
            #"SGD with l1 penalty modified_huber 20",
            #"SGD with l2 penalty modified_huber 20",
            #"SGD with l1 penalty modified_huber 25",
            #"SGD with l2 penalty modified_huber 25",
            #"SGD with l1 penalty modified_huber 50",
            #"SGD with l2 penalty modified_huber 50",
            "Passive-Aggressive 35",
            "Multinomial Naive Bayes - alpha .03"]
 


def main(Articles, classifer, doc_num):
    for j,URL in enumerate(Articles):
        print "Starting Article " + str(j+1)
        Uextractor=URLFeatureExtractor()
        Uextractor.prepareExtractor(URL,doc_num)
        Uextractor.executeExtractor()
        #extractor.predictions(classifier, doc_num)
        Uextractor.runEnsemble(classes)
        artsINFO.append({'html':Uextractor.extracted_html,
                      'text':Uextractor.extracted_text,
                      'predictions': Uextractor.predicts,
                      'tokens':Uextractor.tokens})
        print "Article " + str(j+1) + " Completed"
    #print artsINFO
    return artsINFO
    
if __name__ == "__main__":
    main(Articles,classifier, doc_num)
   
        
   
    


    

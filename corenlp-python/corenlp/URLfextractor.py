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
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.dummy import DummyClassifier
import numpy as np
import scipy as sp
from scipy.sparse import vstack
from sklearn import cross_validation
from sklearn import svm

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

texts={}
collection=None
stemmer = nltk.PorterStemmer()#choice of stemmer
lemmer = WordNetLemmatizer()
dlow_mid_cutoff= 3.48
dmid_high_cutoff=6.10
dsp_dict={}
server = jsonrpclib.Server("http://127.0.0.1:8080")
doc_sets={}
tfidf_bins = {}
offsets=[]

def extract_text_and_html(URL):
    #check if nytimes
    if string.find(URl,'www.nytimes.com')!=-1:
        #double redirect before boilerpipe extraction
        extracted_text,extracted_html=get_NYTimesArticle_Text_and_Html(URL)
    else:
        try:
            #regular boilerpipe extraction
            extracted_text,extracted_html=get_Article_Text_and_Html(URL)
        except:
            #single redirect before boilerpipe extraction
            print 'special article'
            extracted_text,extracted_html=get_SpecialArticle_Text_and_HTMl(URL)
    return extracted_text, extracted_html
def get_SpecialArticle_Text_and_HTMl(URL):
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
            
            extracted_text,extracted_html=get_Article_Text_and_Html(nextLoc)
    
            return extracted_text, extracted_html
    
    
def get_NYTimesArticle_Text_and_Html(URL):
    #NYT
    # get the post data from the link here 
    currLink = URL[string.find(URL, "//")+2:string.find(URL,'com')+3]
    offset = URL[string.find(URL,'com')+3:len(URL)]
    conn0 = httplib.HTTPConnection(currLink)
    conn0.request("GET",offset)
    read0 = conn0.getresponse()
    
    # get the string repsentation of the http response
    data0 = read0.read() # location moved permanently 
    nextLoc = read0.getheader("Location") # find new location from HTTP response
    
    # parse new location
    currLink = nextLoc[string.find(nextLoc, "//")+2:string.find(nextLoc,'com')+3]
    offset = nextLoc[string.find(nextLoc,'com')+3:len(nextLoc)]
    #print "Current link and offset: ", currLink, offset
    
    # retrieve HEAD resposne from link and get new location 
    conn1 = httplib.HTTPConnection(currLink)
    conn1.request("HEAD", offset)
    read1 = conn1.getresponse()
    #print read1.status, read1.reason
    list = read1.getheaders()
    
    # retrieve the new location from head response
    for q in list:
        if q[0] == 'location':
            nextLoc = q[1]
    
            extracted_text,extracted_html=get_Article_Text_and_Html(nextLoc)

            return extracted_text, extracted_html
            
            
def get_Article_Text_and_Html(URL):
    "extract unicode text and html from given URL"
    extractor = Extractor(extractor='ArticleExtractor', url=URL)
    extracted_text = extractor.getText()
    extracted_html = extractor.getHTML()
    return extracted_text,extracted_html

def prepare_extractor(doc_num):
    """
    Prepare feature extractor by preprocessing and storing the lists we are going to use and loading corpus from DB.
    @param doc_num: the total number of documents you want to include in this training and testing
    """
    print 'Execute extractor'
    dsp_dict=preprocess_descriptiveness()
    
    lstfiles=["subjective","report_verb","implicative","hedge","factive","entailment","bias-lexicon","assertive","negative-word", "positive-word"]
    for known_lst in lstfiles:
        # epsb: changing to use dict rather than set
        doc_sets[known_lst] = dict( [(preprocess_each_word(line.strip()), True) 
                for line in open(listspath+known_lst+".txt", 'r')] )
        #self.doc_sets[known_lst]=set([self.preprocessEachWord(line.strip()) for line in open(listspath+known_lst+".txt", 'r')])
      
    #build corpus
    return dsp_dict, doc_sets

def preprocess_descriptiveness():
    """
    Preprocess Decriptiveness list for later use
    """
    dfile  = open(listspath+"ImageryRatings.csv", "rb")
    reader = csv.reader(dfile)
    next(reader, None)

    for row in reader:
    # Save header row.
        word=stemmer.stem((row[0].lower()))
        count=row[1]
        category=0.66  #"mid"
        if(count < dlow_mid_cutoff):
            category=0.33 #'low'
        elif(count > dmid_high_cutoff):
            category=1 #"high"
        dsp_dict[word]=category
    return dsp_dict
    

def generate_feature_lists(text,doc_num):
    features=[]
    coreParsed=[]
    dsp_dict, doc_sets=prepare_extractor(doc_num)
    rowNum,texts,collection=addTOcorpusFromDB(doc_num,text)
    separate=text.split('\n',1)
    print "Extracting features..."
    title_words=[stemmer.stem(lemmer.lemmatize(w)) for w in nltk.wordpunct_tokenize(separate[0])]
    print 'parsing...'
    coreParsed=extract_sentence_info(text)
    for i in range(len(coreParsed)):
            #sent=self.coreParsed[doc_id][i]['text']
        tuples=coreParsed[i]['dependencies']
            #pprint(tuples)
        words=coreParsed[i]['words'] #words are words properties
        for windex in range(len(words)):
            #ignore punctuations
            if filterWord(words[windex][0]):
                continue 
    
            f1=generate_features(windex,words,title_words,text,rowNum,texts,collection,dsp_dict, doc_sets)
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
    return features



def extract_sentence_info(text):
    """
    Extract information of a text using stanford corenlp
    @param text: the input text
    """
    sents=nltk.sent_tokenize(text)
    currTotal=0
    sent_index = 0
    coreParsed=[]
    for sent in sents:
        result=server.parse(sent)
        newlsts=(loads(result))['sentences']
        if  not coreParsed:
            coreParsed=newlsts
        else:
            coreParsed.extend(newlsts)
        #sent_len=int(newlsts[-1]['words'][-1][1]['CharacterOffsetEnd'])
        sent_len = \
                int(coreParsed[sent_index]['words'][-1][1]['CharacterOffsetEnd'])

        offsets.extend([currTotal for k in 
                range(len(coreParsed[sent_index]))])

        #pprint(newlsts)
        currTotal+=sent_len
        sent_index += 1
        #assert(sent_len==len(sent)),('parsed_leng %d != expected %d '%(sent_len, len(sent)))
    return coreParsed

def filterWord(word):
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


def generate_features(outer_index, words,title_words, text,rowNum,texts,collection,dsp_dict, doc_sets):
    """
    Generate feature vectors for words in a sentence.
    @param words: all the words in a sentence.
    @param outer_index: the word position in the sentence
    """
    features = {}
    tokens = ['^^^']
    lemmas = ['^^^']
    stems=['^^^']
    entities=['^^^']
    for wls in words:
        #text.append(self.preprocessEachWord(wls[0]))
        tokens.append(wls[0].lower())
        lemmas.append(wls[1]['Lemma'])
        stems.append(preprocess_each_word(wls[0]))
        entities.append(wls[1]['NamedEntityTag'])
    tokens.append("^^^")
    lemmas.append("^^^")
    stems.append("^^^")
    entities.append('^^^')
    
    index = outer_index + 1 # adjust for initial and terminal strings
    
    fnames = [] # this is our list of feature names
    
    if feat_words:
        '''
        # use the token and lemma (and +/- 1,2) features
        fnames.extend(["token", "token: -1",  'token +1', "token: -2", 'token +2'])
        features['token'] = tokens[index]
        plusMinus_features_list('token', 1, tokens, index, features, True)
        plusMinus_features_list('token', 2, tokens, index, features, True)
        '''
        fnames.extend(['lemma', 'lemma: -1', 'lemma: +1', 'lemma: -2', 'lemma: +2'])
        features['lemma'] = lemmas[index]
        plusMinus_features_list('lemma', 1, lemmas, index, features, True)
        plusMinus_features_list('lemma', 2, lemmas, index, features, True)
        
        fnames.extend(['bigram -1', 'bigram +1', 'trigram -1', 'trigram 0', 'trigram +1'])
        
        # bigrams
        # ignore bigrams that include stopwords, punctuation, and numbers
        if index > 0:
            if filterWord(lemmas[index-1]):
                features['bigram -1'] = 'null'
            else:
                features['bigram -1'] = lemmas[index-1] + ' ' + lemmas[index]
        else:
            features['bigram -1'] = 'null'
        if index < len(lemmas) - 1:
            if filterWord(lemmas[index+1]):
                features['bigram -1'] = 'null'
            else:
                features['bigram +1'] = lemmas[index] + ' ' + lemmas[index+1]
        else:
            features['bigram +1'] = 'null'
        
        # trigrams
        # ignore trigrams that include stopwords, punctuation, and numbers
        if index > 1:
            if filterWord(lemmas[index-2]) or filterWord(lemmas[index-1]):
                features['trigram - 1'] = 'null'
            else:
                features['trigram - 1'] = lemmas[index - 2] + ' ' + lemmas[index - 1] \
                        + lemmas[index]
        else:
            features['trigram - 1'] = 'null'
        if index > 0 and index < len(lemmas) - 1:
            if filterWord(lemmas[index-1]) or filterWord(lemmas[index+1]):
                features['trigram 0'] = 'null'
            else:
                features['trigram 0'] = lemmas[index - 1] + ' ' + lemmas[index] + ' ' + \
                        lemmas[index + 1]
        else:
            features['trigram 0'] = 'null'
        if index < len(lemmas) - 2:
            if filterWord(lemmas[index+1]) or filterWord(lemmas[index+2]):
                features['trigram +1'] = 'null'
            else:
                features['trigram +1'] = lemmas[index] + ' ' + lemmas[index + 1] + ' ' + \
                        lemmas[index + 2]
        else:
            features['trigram +1'] = 'null'
    
    if feat_POS:
        # use the POS, POS +/- 1, and POS +/- 2 features
        fnames.extend(["pos", "pos -1", 'pos +1',  "pos -2", 'pos +2'])
        
        poses=['BEG']
        for wls in words:
            poses.append(wls[1]['PartOfSpeech'])
        poses.append('END')
        
        features['pos'] = poses[index]
        plusMinus_features_list('pos', 1, poses, index, features)
        plusMinus_features_list('pos', 2, poses, index, features)
    
    if feat_entity:
        # use the type of named entity as a feature
        fnames.extend(['entity type', 'entity bigram - 1', 'entity bigram + 1', 
                'entity trigram - 1', 'entity trigram 0', 'entity trigram + 1'])
        features['entity type'] = entities[index]
        plusMinus_features_list('entity type', 1, entities, index, features)
        plusMinus_features_list('entity type', 2, entities, index, features)
    '''
        # performance drops a tiny bit for logistic regression when using entity n-grams
        # entity bigrams
        if index > 0:
            if filterWord(lemmas[index-1]):
                features['entity bigram - 1'] = 'null'
            else:
                features['entity bigram - 1'] = entities[index-1] + ' ' + entities[index]
        else:
            features['entity bigram - 1'] = 'null'
        if index < len(entities) - 1:
            if filterWord(lemmas[index+1]):
                features['entity bigram + 1'] = 'null'
            else:
                features['entity bigram + 1'] = entities[index] + ' ' + entities[index+1]
        else:
            features['entity bigram + 1'] = 'null'
        
        # entity trigrams
        if index > 1:
            if filterWord(lemmas[index-2]) or filterWord(lemmas[index-1]):
                features['entity trigram - 1'] = 'null'
            else:
                features['entity trigram - 1'] = entities[index-2] + ' ' + entities[index-1] +\
                        ' ' + entities[index]
        else:
            features['entity trigram - 1'] = 'null'
        if index > 0 and index < len(entities) - 1:
            if filterWord(lemmas[index-1]) or filterWord(lemmas[index+1]):
                features['entity trigram 0'] = 'null'
            else:
                features['entity trigram 0'] = entities[index-1] + ' ' + entities[index] +\
                        ' ' + entities[index+1]
        else:
            features['entity trigram 0'] = 'null'
        if index < len(entities) - 2:
            if filterWord(lemmas[index+1]) or filterWord(lemmas[index+2]):
                features['entity trigram + 1'] = 'null'
            else:
                features['entity trigram + 1'] = entities[index] + ' ' + entities[index+1] +\
                        ' ' + entities[index+2]
        else:
            features['entity trigram + 1'] = 'null'
       '''
    
    if feat_sent_len:
        # use the sentence length feature
        fnames.extend(['sentence length:', 'sentence position:'])
        features['sentence length:']=len(words)
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
        features['InTitle'] = int(stems[index] in title_words)
    
    if feat_TFIDF:
        # use TFIDF as a feature
        fnames.extend(['TFIDF'])
        features['TFDIF']=TFIDF(stems[index],texts[rowNum],collection)
    
    if feat_imagery:
        # use the imagery/descriptiveness rating feature
        fnames.extend(['descriptiveness', 'descriptiveness +1', 'descriptiveness -1', 
                'descriptiveness +2', 'descriptiveness -2', 'descriptiveness average'])
        
        try:
            features['descriptiveness'] = dsp_dict[stems[index]]
        except KeyError:
            features['descriptiveness'] = 'null'
        plusMinus_features_dict('descriptiveness', 1, stems, dsp_dict, index, 
                features)
        plusMinus_features_dict('descriptiveness', 2, stems, dsp_dict, index, 
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
        else:
            features['descriptiveness average'] = 'null'
        for i in range(1,3):
            features.pop("descriptiveness: -%d" % i)
            features.pop("descriptiveness: +%d" % i)
        
    
    if feat_word_lists:
        # use the special lists of words (factives, implicatives, etc.)
        for known_set in doc_sets.keys():
            fnames.append(known_set)
            
            features[(known_set)] = stems[index] in doc_sets[known_set]
            plusMinus_features_dict(known_set, 1, stems, doc_sets[known_set],
                    index, features)
            plusMinus_features_dict(known_set, 2, stems, doc_sets[known_set],
                    index, features)
            features[known_set + " in context"] = features[known_set + ": +1"] or \
                    features[known_set + ": -1"] or features[known_set + ": +2"] or \
                    features[known_set + ": -2"]
            for i in range(1,3):
                features.pop(known_set + ": -%d" % i)
                features.pop(known_set + ": +%d" % i)
    return features
    

def preprocess_each_word(word):
    """
    Implement any preprocessing needed to be done for each word	
    """
    return stemmer.stem(word.lower())    

def plusMinus_features_list(fname, offset, values_list, index, features, filter=False):
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
                if filterWord(values_list[index - offset]):
                    features[fname + ": -%d" % offset] = 'null'
                else:
                    features[fname + ": -%d" % offset] = values_list[index - offset]
            else:
                features[fname + ": -%d" % offset] = values_list[index - offset]
        else:
            features[fname + ": -%d" % offset] = 'null'
            
        if index < len(values_list) - offset:
            if filter:
                if filterWord(values_list[index + offset]):
                    features[fname + ": +%d" % offset] = 'null'
                else:
                    features[fname + ": +%d" % offset] = values_list[index + offset]
            else:
                features[fname + ": +%d" % offset] = values_list[index + offset]
        else:
            features[fname + ": +%d" % offset] = 'null'
    
def plusMinus_features_dict(fname, offset, key_list, values_dict, index, features):
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
    
    if index > 0:
        try:
            features[fname + ": -%d" % offset] = values_dict[key_list[index - offset]]
        except KeyError:
            features[fname + ": -%d" % offset] = 'null'
    else:
        features[fname + ": -%d" % offset] = 'null'
    if index < len(key_list) - offset:
        try:
            features[fname + ": +%d" % offset] = values_dict[key_list[index + offset]]
        except KeyError:
            features[fname + ": +%d" % offset] = 'null'
    else:
        features[fname + ": +%d" % offset] = 'null'



def addTOcorpusFromDB(doc_num,text):
    """
    Build corpus from data in DB
    @param doc_num: the number of docs you are gonna use
    """
    #db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation')
    #c=db.cursor()
    ## we only want documents that have at least three valid annotations
    #c.execute("SELECT  doc_id, doc_html, sum(valid) as tot_valid FROM Documents natural join Annotations WHERE doc_id > 1 group by doc_id having tot_valid >= 3 order by doc_id desc LIMIT %s "%(doc_num,))#a_id > 125")
    ##c.execute("select doc_id, doc_html from Documents where doc_id > 1 order by doc_id desc LIMIT %s"%(doc_num,))
    #
    #rowall=c.fetchall()
    #rowsTaken=[]
    #for row in rowall:
    #    doc=nltk.clean_html(row[1])
    #    texty=nltk.Text([preprocess_each_word(w) for w in nltk.wordpunct_tokenize(doc) if len(w) >= 1 and not all(a in string.punctuation for a in w)])
    #    texts[int(row[0])]=texty
    #    rowsTaken.append(row[0])
    f = open('texts.pickle')
    texts=pickle.load(f)
    f.close()
    newText=nltk.Text([preprocess_each_word(w) for w in nltk.wordpunct_tokenize(text) if len(w) >= 1 and not all(a in string.punctuation for a in w)])
    texts[5]=newText
    rowNum=5
    collection=nltk.TextCollection(texts.values())
    return rowNum, texts, collection
  
def TFIDF(word,document,collection):
    """
    Calculate the tf_idf bin of a WORD in a certain DOCUMENT in our corpus
    @param: the target word
    @param: the target document
    """
    if document not in tfidf_bins:
        tfidf_bins[document] = {}
        # get the tfidf scores for all tokens in this document
        token_freq = [(collection.tf_idf(w, document), collection.tf(w,document), 
                    collection.idf(w, document), w) for w in document.vocab().samples() if not all(a in string.punctuation for a in w)]
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
            tfidf_bins[document][token] = cur_bin
        
    return tfidf_bins[document].get(word, 8) # use this so punct get the max tfidf bin


def loadModel(type):
    """
    load the saved model
    @param type: the type of the classifier you are loading
    """
    f = open(type+'_classifier.pickle')
    model=pickle.load(f)
    f.close()
    return model

def extractFeatures(extracted_text, doc_num):
    print "Article text extracted"
    feat=generate_feature_lists(extracted_text,doc_num)
    print "Features Extracted"
    return feat

def predictions(classifier, feat, doc_num):
    clf=loadModel(classifier)
    g=open("vec.pickle")
    vec = pickle.load(g)
    g.close()
    print "Predicting..."
    featureData=vec.transform(feat)
    #print featureData
    preds=clf.predict(featureData)
    predProbs=clf.predict_proba(featureData)
    lenientPred=[]
    results=[]
    probResults=[]
    for p,f in enumerate(feat):
        results.append([f['lemma'],preds[p]])
        probResults.append([f['lemma'],predProbs[p][1]])
        if predProbs[p][1]>=0.33:
            lenientPred.append(1)
        else:
            lenientPred.append(0)
    return preds,lenientPred, results, probResults

URL1="http://articles.chicagotribune.com/2008-09-27/news/0809260511_1_blagojevich-administration-lucio-guerrero-blagojevich-spokesman"
URL2="http://www.huffingtonpost.com/rj-eskow/obama-could-appoint-a-peo_b_5452814.html?utm_hp_ref=politics"
URL3="http://www.dailykos.com/story/2014/06/17/1307586/-Guess-who-this-North-Carolina-Republican-means-by-the-traditional-population"
URL4="http://www.cnsnews.com/news/article/ali-meyer/price-index-meats-poultry-fish-eggs-rockets-all-time-high"
URL5="http://www.politico.com/story/2014/06/clinton-library-memos-kyoto-protocol-china-india-107545.html"
Articles=[URL1, URL2, URL3, URL4, URL5]
classifier='Logistic Classifier'
doc_num='10'
html=[]
text=[]
preds=[]
def main(Articles, classifer, doc_num):
    for j,URL in enumerate(Articles):
        print "Starting Article " + str(j+1)
        extracted_text,extracted_html=get_Article_Text_and_Html(URL)
        feat=extractFeatures(extracted_text, doc_num)
        pred,lenientPred,results,probResults =predictions(classifier, feat, doc_num)
        print pred
        print lenientPred
        html.append(extracted_html)
        text.append(extracted_text)
        preds.append(pred)
        print "Article " + str(j+1) + " Completed"
    return html,text, preds 
    
if __name__ == "__main__":
    main(Articles,classifier, doc_num)
   
        
   
    


    
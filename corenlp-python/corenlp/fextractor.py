#Different Feature Extractors
#@Author: Crystal Qin
from __future__ import division
import nltk, MySQLdb,jsonrpclib
import sys, re,random,os,time,string
from pprint import pprint
import csv, collections
from json import loads
from corenlp import batch_parse
from bisect import bisect_left, bisect_right
import pickle

#nltk imports
from nltk.stem.wordnet import WordNetLemmatizer
import nltk.classify.util # for accuracy & log_likelihood
import nltk.metrics
#from corenlp import StanfordCoreNLP


#sklearn imports
from time import time
import pylab as pl



from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.utils.extmath import density
from sklearn import metrics
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import GaussianNB
import numpy as np
from sklearn import cross_validation
from sklearn import svm

#experiment with stop words and puncts
#python corenlp/corenlp.py -H localhost -p 3455 -S stanford-corenlp-full-2013-06-20/
#python corenlp/corenlp.py -S stanford-corenlp-full-2013-06-20/
#python corenlp/fextractor.py
# cd /cygdrive/c/users/qin/cs_projects/tortoise/Research/corenlp-python
# training with 20, 30 and 50 randomly selected dataset
# using annotation randomly to test. 
# other classifiers decision trees 
# logistical regression

# googling around, http://scikit-learn.org/stable/
#JUST the lists -- baseline test
#overall precisions/recalls and subsets
#train over 45 set of documents and test on 5 documents the other way around
listspath='lists/'
rm_invdata=True
baseline=False
CV=False
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

        #data sets:
        self.X_train=None
        self.X_test=None
        self.y_train=None
        self.y_test=None
        self.feature_names=None

    
        
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
        featuresets,targets=self.train_model()
        print "Got train_set, start training models"
        vec = DictVectorizer()
        feature_data=vec.fit_transform(featuresets)
        print 'done transforming feature data'
        #randomized
        if CV:
            self.crossValidation(5, feature_data, targets)
        else:
            self.X_train, self.X_test, self.y_train, self.y_test = cross_validation.train_test_split(feature_data, targets, test_size=0.1, random_state=len(targets))
            print 'done splitting sets'
            self.feature_names=np.asarray(vec.get_feature_names())
            self.runAllClassifiers()

    def crossValidation(self, nfold, X, Y):
        from sklearn.cross_validation import KFold
        kf=KFold(len(self.y_train), n_folds=nfold, indices=True)
        counter=0
        for train, test in kf:
            self.X_train, self.X_test, self.y_train, self.y_test=X[train], X[test], Y[train], Y[test]
            print 'fold %d \n\n'%counter
            self.runTopClassifiers()
            counter+=1


    # Benchmark classifiers
    def benchmark(self, clf):

        print('_' * 80)
        print("Training: ")
        print(clf)
        t0 = time()
        clf.fit(self.X_train, self.y_train)
        train_time = time() - t0
        print("train time: %0.3fs" % train_time)

        t0 = time()
        pred = clf.predict(self.X_test)
        test_time = time() - t0
        print("test time:  %0.3fs" % test_time)

        f1_score = metrics.f1_score(self.y_test, pred)
        acc_score=metrics.accuracy_score(self.y_test,pred)
        precision_score=metrics.precision_score(self.y_test,pred)
        recall_score=metrics.precision_score(self.y_test, pred)
        print("f1-score:   %0.3f" % f1_score)
        print("acc-score: %0.3f" % acc_score)
        print('precision-score: %0.4f' %precision_score)
        print('recall-score: %0.4f' %recall_score)

        if hasattr(clf, 'coef_'):
            print("dimensionality: %d" % clf.coef_.shape[1])
            print("density: %f" % density(clf.coef_))

            if self.feature_names is not None:
                print("top 10 keywords per class:")

                top10 = np.argsort(clf.coef_[0])[-10:]
                print("%s" % (" ".join(self.feature_names[top10])))
            print()


        print("classification report:")
        print(metrics.classification_report(self.y_test, pred, target_names=['class 0', 'class 1']))


        print("confusion matrix:")
        print(metrics.confusion_matrix(self.y_test, pred))

        print()
        clf_descr = str(clf).split('(')[0]
        return clf_descr, f1_score, acc_score, precision_score, recall_score, train_time, test_time

    def runTopClassifiers(self):
        '''Top determined by running all classifiers on dataset of size 20'''
        results=[]

    def runAllClassifiers(self):
        results = []
        for clf, name in (
                (RidgeClassifier(tol=1e-2, solver="lsqr"), "Ridge Classifier"),
                (Perceptron(n_iter=50), "Perceptron"),
                (PassiveAggressiveClassifier(n_iter=50), "Passive-Aggressive")):#,(KNeighborsClassifier(n_neighbors=10), "kNN")
            print('=' * 80)
            print(name)
            results.append(self.benchmark(clf))

        for penalty in ["l2", "l1"]:
            print('=' * 80)
            print("%s penalty" % penalty.upper())
            # Train Liblinear model
            results.append(self.benchmark(LinearSVC(loss='l2', penalty=penalty,
                                                    dual=False, tol=1e-3)))

            # Train SGD model
            results.append(self.benchmark(SGDClassifier(alpha=.0001, n_iter=50,
                                                   penalty=penalty)))

        # Train SGD with Elastic Net penalty
        print('=' * 80)
        print("Elastic-Net penalty")
        results.append(self.benchmark(SGDClassifier(alpha=.0001, n_iter=50,
                                               penalty="elasticnet")))

        # Train NearestCentroid without threshold
        print('=' * 80)
        print("NearestCentroid (aka Rocchio classifier)")
        results.append(self.benchmark(NearestCentroid()))

        # Train sparse Naive Bayes classifiers
        print('=' * 80)
        print("Naive Bayes")
        results.append(self.benchmark(MultinomialNB(alpha=.01)))
        results.append(self.benchmark(BernoulliNB(alpha=.01)))


        class L1LinearSVC(LinearSVC):

            def fit(self, X, y):
                # The smaller C, the stronger the regularization.
                # The more regularization, the more sparsity.
                self.transformer_ = LinearSVC(penalty="l1",
                                              dual=False, tol=1e-3)
                X = self.transformer_.fit_transform(X, y)
                return LinearSVC.fit(self, X, y)

            def predict(self, X):
                X = self.transformer_.transform(X)
                return LinearSVC.predict(self, X)

        #print('=' * 80)
        #print("LinearSVC with L1-based feature selection")
        #esults.append(self.benchmark(L1LinearSVC()))


        # make some plots
    def drawDiagram(self, results):
        indices = np.arange(len(results))

        results = [[x[i] for x in results] for i in range(5)]

        clf_names, f1_score, acc_score, precision_score, recall_score = results
        #training_time = np.array(training_time) / np.max(training_time)
        #test_time = np.array(test_time) / np.max(test_time)

        pl.figure(figsize=(12,8))
        pl.title("Score")
        pl.barh(indices, f1_score, .2, label="f1", color='r')
        pl.barh(indices+ .3, acc_score, .2, label='accuracy', color='y')
        pl.barh(indices+ .56, precision_score, .2, label='precision', color='m')
        pl.barh(indices+ .76, recall_score, .2, label='recall', color='c')
        #pl.barh(indices + .3, training_time, .2, label="training time", color='g')
        #pl.barh(indices + .6, test_time, .2, label="test time", color='b')
        pl.yticks(())
        pl.legend(loc='best')
        pl.subplots_adjust(left=.25)
        pl.subplots_adjust(top=.95)
        pl.subplots_adjust(bottom=.05)

        for i, c in zip(indices, clf_names):
            pl.text(-.3, i, c)

        pl.show()

    def preprocessDescriptiveness(self):
   
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


                

    
    def corpusFromDB(self):
        db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation')
        c=db.cursor()
        c.execute("SELECT  DISTINCT(doc_id),doc_html FROM Documents natural join Annotations WHERE doc_id != 1 LIMIT 20 ")#a_id > 125")
        
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

            #pprint(newlsts)
            currTotal+=sent_len
            #assert(sent_len==len(sent)),('parsed_leng %d != expected %d '%(sent_len, len(sent)))
        
        
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
        if not baseline:
            global dsp_dict
            fnames=["word", "word: -1",  'word +1', "word: -2", 'word +2',"pos", "pos -1", 'pos +1',  "pos -2", 'pos +2', "sentence length:", 'descriptiveness:%d', 'isInTitle:%d', 'TFIDF:']
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
            features[fnames[1]]=text[index-1]
            features[fnames[2]]=text[index+1]

            features[fnames[5]]=poses[index]
            features[fnames[6]]=poses[index-1]
            features[fnames[7]]=poses[index+1]


            if(index>1):
                features[fnames[3]]=text[index-2]
                features[fnames[8]]=text[index-2]
            else:
                features[fnames[3]]='null'
                features[fnames[8]]='null'

            if(index<len(poses)-2):
                features[fnames[4]]=text[index+2]
                features[fnames[9]]=text[index+2]
            else:
                features[fnames[4]]="null"
                features[fnames[9]]="null"





            features[fnames[10]]=len(words)

            # the word's -2, -1, 0, 1, 2
            for i in range(-2, 3):
                #print text[index+i]
                if (index+i) >0 and (index+i) < len(text) and text[index+i] in self.dsp_dict:
                    features[fnames[11]%i]= self.dsp_dict[text[index+i]]
                else:
                    features[fnames[11]%i]=0 # not in descriptive list

            features[fnames[12]]=int(text[index] in self.title_words)
            features[fnames[13]]=self.TFIDF(text[index],self.texts[self.docID])
        
        # all the lists
        for known_set in self.doc_sets.keys():
            features[("is "+known_set)]=int(text[index] in self.doc_sets[known_set])

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
                #print '%d %d %d %d\n'%(self.start_indices[i][start_pos], end_val, cstart, cend)
                return 1
        if end_pos < len(self.end_indices[i]):
            start_val=self.start_indices[i][end_pos]
            #assert(end_pos < len(self.start_indices[i])),('end_pos %d endi size %d, starti size %d, ')
            if start_val <= cend:
                #print '%d %d %d %d\n'%(start_val, self.end_indices[i][end_pos], cstart, cend)
                return 1
        return 0
        
                
            

    def train_model(self):
        
        invalid_ann={52:[225,224], 104:[224, 225], 148:[225,224],146:[224, 225],118:[167,153], 174:[167,153],68: [167],166:[167,153],39:[167,153]}
        train_set=[]
        targets=[]
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
            
            c.execute('SELECT char_annotation, a_id from Annotations WHERE doc_id = %s'%(doc_id,))
            rows=c.fetchall()

            num_ann=len(rows)
            self.start_indices=[]
            self.end_indices=[]

            for i in range(num_ann):
                indexStr=rows[i][0]

                if indexStr is None or (rm_invdata and doc_id in invalid_ann and rows[i][1] in invalid_ann[doc_id]):
                    print 'invalide annotation %d %d ignored'%(doc_id, rows[i][1])
                    continue
                self.start_indices.append([])
                self.end_indices.append([])
                isents=indexStr.split('.')
                del isents[-1]
                for sentInd in isents:
                    il=sentInd.split(" ")
                    self.start_indices[-1].append(int(il[0])) #title??
                    self.end_indices[-1].append(int(il[1]))
                #pprint (self.coreParsed[0])
            #pprint(self.start_indices)
            #pprint(self.end_indices)
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
                            f1["dependency: %s %s"%(rel, 'gov')]=1
                        elif thew == sub:
                            f1["dependency: %s %s"%(rel,'sub')]=1
                        #else:
                            #f1["dependency: %s %s"%(rel,'sub')]=False
                            #f1["dependency: %s %s"%(rel, 'gov')]=False
                        for a in range(len(self.start_indices)):
                            train_set.append(f1)
                            #pprint(f1)
                            targets.append(self.isHighlighted(int(words[windex][1]['CharacterOffsetBegin'])+self.offsets[i],int(words[windex][1]['CharacterOffsetEnd'])+self.offsets[i],a))
            

        return (train_set,targets)
        
                            
def saveModel(classifier, type='nb'):

    f = open(type+'_classifier.pickle', 'wb')
    pickle.dump(classifier, f)
    f.close()

def loadModel(type='nb'):
    f = open(type+'_classifier.pickle')
    model=pickle.load(f)
    f.close()
    return model

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

# NLP Tool to train and test Political Framing Words Classifiers
# Including:Feature Extractors, Model training and performance evaluation
#@Author: Crystal Qin
#Note: referenced some code from http://scikit-learn.org/stable/ User Guide and Examples
from __future__ import division
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
from sklearn.dummy import DummyClassifier
import numpy as np
import scipy as sp
from scipy.sparse import vstack
from sklearn import cross_validation
from sklearn import svm



#python corenlp/corenlp.py -S stanford-corenlp-full-2013-06-20/
#could also specify port number if want: python corenlp/corenlp.py -H localhost -p 3455 -S stanford-corenlp-full-2013-06-20/
#python corenlp/fextractor.py 50 > results.txt


listspath='lists/'

rm_invdata=True # whether or not rm possible invalid annotations
CV= True # whether or not do cross-validation on the top classifier
doc_level=True

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


class FeatureExtractor(object):
    """
    NLP Tool to train and test Political Framing Words Classifiers
    """
    
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
        self.tfidf_bins = {}
        
        #doc specific
        self.docID=0
        self.title_words=[]
        self.coreParsed=[]#the sentences(containing all its information by stanford corenlp) of this text
        self.offsets=[] #the start char offset for each sentence in this doc.
                        #i.e corenlp generated char offset+self.offsets[i]=char_annotation start index from database
        #for all anotations of this doc
        self.start_indices=[] # format[[a1_s1, a1_s2, a1_s3...], [a2_s1, a2_s2, a3_s3... ] ...]
                             #ai_sj: means this doc's annotation i's jth highlighting's start index
        self.end_indices=[] #same format as above but for the end indices

        #data sets:
        self.X_train=None
        self.X_test=None
        self.y_train=None
        self.y_test=None
        self.feature_names=None

    
    
    def prepareExtractor(self,doc_num):
	"""
	Prepare feature extractor by preprocessing and storing the lists we are going to use and loading corpus from DB.
	@param doc_num: the total number of documents you want to include in this training and testing
	"""
        print 'execute extractor'
        self.preprocessDescriptiveness()

        lstfiles=["subjective","report_verb","implicative","hedge","factive","entailment","bias-lexicon","assertive","negative-word", "positive-word"]
        for known_lst in lstfiles:
            # epsb: changing to use dict rather than set
            self.doc_sets[known_lst] = dict( [(self.preprocessEachWord(line.strip()), True) 
                    for line in open(listspath+known_lst+".txt", 'r')] )
            #self.doc_sets[known_lst]=set([self.preprocessEachWord(line.strip()) for line in open(listspath+known_lst+".txt", 'r')])
          
        #build corpus
        self.corpusFromDB(doc_num)

    
    def executeExtractor(self, parses_file=None):
	"""
	Generate features and labels using training data. Then partition the data either doc_level or word_level, running all classifiers
        on it to test performance.Using cross validation if CV bit is turned on 	
	"""
        global CV, doc_level
        featuresets,targets, doc_offsets=self.generate_feature_datasets()# featuresets are all the feature vectors, targets are all the labels
        if parses_file:
            # save the parses
            outfile = open(parses_file, 'w')
            cPickle.dump(self.coreParsed, outfile)
            outfile.close()
        print "Got train_set, start training models"
        vec = DictVectorizer()
        feature_data=vec.fit_transform(featuresets) # the sparse matrix of 0-1 values
        print 'done transforming feature data'
        self.feature_names=np.asarray(vec.get_feature_names()) #the feature names for the sparse matrix values
        if doc_level:
            random.seed(123456)
            docs_to_use = doc_offsets.keys()
            if CV:
                self.crossValidation(10, feature_data, docs_to_use, targets, doc_offsets)
            else:
                random.shuffle(docs_to_use)
                size = int(len(docs_to_use) * 0.5)
                pprint (feature_data)
                labels=[]
                train_fs=[]
                for did in docs_to_use[:size]:
                    start, end=doc_offsets[did]
                    train_fs.append((start, end))
                    labels.extend(targets[start:end])


                self.X_train=vstack([feature_data[s:t] for s, t in train_fs])
                self.y_train=np.asarray(labels)

                labels=[]
                test_fs=[]
                for did in docs_to_use[size:]:
                    start, end=doc_offsets[did]
                    test_fs.append((start, end))
                    labels.extend(targets[start:end])
                self.X_test=vstack([feature_data[s:t] for s, t in test_fs])
                self.y_test=np.asarray(labels)
                self.runAllClassifiers()

        else:

            #randomized
            if CV:
                self.crossValidation(10, feature_data, np.asarray(targets))
            else:
                self.X_train, self.X_test, self.y_train, self.y_test = cross_validation.train_test_split(feature_data, targets, test_size=0.1, random_state=0)
                print 'done splitting sets'
                self.runAllClassifiers()
                #self.drawDiagram()

    
    def crossValidation(self, nfold, X, Y, targets=None, doc_offsets=None):
	"""
	Do cross validation on the feature data sets
	@param X: the list of features
        @param Y: In word_level, the list of labels; In doc_level, list of doc_ids 
	@param targets:In word_level, None; In doc_level, the actual labels
	@param doc_offsets: In word_level, None; In doc_level, the offsets generated by self.generate_feature_datasets() method
	"""
        from sklearn.cross_validation import KFold, ShuffleSplit, StratifiedKFold
        global doc_level
        
        #kf=KFold(len(Y), n_folds=nfold, shuffle=True, random_state=0, indices=True)
        kf=ShuffleSplit(len(Y), n_iter=nfold, test_size=2.0/(nfold), random_state=0)
        #kf = StratifiedKFold(Y, n_folds=nfold)
        
        counter=0
        mean={}
        corrs = {} # correlations between avg predictions and avg annotations
        for train, test in kf:
            if doc_level:

                train_fs=[]
                labels=[]
                for ind in train:
                    did=Y[ind]
                    start, end=doc_offsets[did]
                    train_fs.append((start, end))
                    labels.extend(targets[start:end])

                self.X_train=vstack([X[s:t] for s, t in train_fs])
                self.y_train=np.asarray(labels)

                labels=[]
                test_fs=[]
                # for ind in train: # epsb thinks this is an error
                for ind in test:
                    did=Y[ind]
                    start, end=doc_offsets[did]
                    test_fs.append((start, end))
                    labels.extend(targets[start:end])
                self.X_test=vstack([X[s:t] for s, t in test_fs])
                self.y_test=np.asarray(labels)

            else:
                self.X_train, self.X_test, self.y_train, self.y_test=X[train], X[test], Y[train], Y[test]

            print 'fold %d \n\n'%counter
            results=self.runAllClassifiers()
            """
            # store the correlations from this fold
            for result in results:
                if result[0] not in corrs:
                    corrs[result[0]] = {}
                cur_start_offset = 0 # for keeping track of doc offsets in predictions
                for nth_doc in test:
                    doc_id = doc_offsets.keys()[nth_doc]
                    #doc_len = int( (doc_offsets[doc_id][1] - doc_offsets[doc_id][0]) / 5 )
                    doc_len = doc_offsets[doc_id][1] - doc_offsets[doc_id][0]
                    # get all the annotations (i.e., targets) for this doc
                    doc_ations = targets[doc_offsets[doc_id][0]:doc_offsets[doc_id][1]]
                    all_preds = list(result[7])
                    doc_preds = all_preds[cur_start_offset:cur_start_offset + doc_len]
                    corrs[result[0]][doc_id] = sp.stats.pearsonr(doc_ations, doc_preds)
                    
                    cur_start_offset += doc_len

                    # NB: the following was required when training on each annotation separately. 
                    # not required when training on binned annotations averages.
                    '''
                    # determine the average annotations (i.e., targets) for this doc
                    avg_ations = [0] * doc_len
                    for i in range(0,5):
                        for j in range(0,doc_len):
                            avg_ations[j] += doc_ations[i::5][j]
                    avg_ations = [a / 5.0 for a in avg_ations]
                    
                    # determine the average predictions for this document
                    avg_preds = [0] * doc_len
                    all_preds = list(result[7]) # classifier's predictions
                    for i in range(0,5):
                        for j in range(0,doc_len):
                            avg_preds[j] += all_preds[i::5][j]
                    avg_preds = [a / 5.0 for a in avg_preds]
                    
                    # key is classifier's name
                    corrs[result[0]][doc_id] = sp.stats.pearsonr(avg_ations, avg_preds)
                    '''
            """
            for x in results:
                if x[0] not in mean:
                    mean[x[0]] = [0,0,0,0]
                for ind in range(4):
                    mean[x[0]][ind]+=x[ind+1]
            '''
            if not mean:
                mean={x[0]:[x[1],x[2],x[3],x[4]] for x in results}
            else:
                for tuple in results:
                    for ind in range(4):
                        mean[tuple[0]][ind]+=tuple[ind+1]
            '''
            counter+=1
        
        # print average performance across all folds
        for key, val in mean.items():
            print('_' * 80)
            print 'avg for %s'%(key)
            print 'f1: %f'% (val[0]/len(kf))
            print 'acc: %f'%(val[1]/len(kf))
            print 'precision: %f'%(val[2]/len(kf))
            print 'recall: %f'%(val[3]/len(kf))
            """
            correls = [cor[0] for cor in corrs[key].values() if not np.isnan(cor[0])]
            if len(correls) > 0:
                print 'avg correlation: %f'%(np.mean(correls))
                print 'min correlation: %f' % min(correls)
                print 'max correlation: %f' % max(correls)
            """

   
    def benchmark(self, clf):
	"""
	Benchmark classifier by evaluating and printing out it's train time, test time, 
	f1-score, acc-score, precision-score, recall-score, etc.
        @param clf: the classifier to benchmark
	"""

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

        f1_score = metrics.f1_score(self.y_test, pred, pos_label=1, average='weighted')
        acc_score=metrics.accuracy_score(self.y_test,pred)
        precision_score=metrics.precision_score(self.y_test,pred, pos_label=1, average='weighted')
        recall_score=metrics.recall_score(self.y_test, pred, pos_label=1, average='weighted')
        print("f1-score:   %0.3f" % f1_score)
        print("acc-score: %0.3f" % acc_score)
        print('precision-score: %0.4f' %precision_score)
        print('recall-score: %0.4f' %recall_score)

        if hasattr(clf, 'coef_'):
            print("dimensionality: %d" % clf.coef_.shape[1])
            print("density: %f" % density(clf.coef_))

            if self.feature_names is not None:
                nf=50
                print("top %d keywords per class:"%(nf))

                self.show_most_informative_features(clf.coef_[0],nf)
                #top10 = np.argsort(clf.coef_[0])[-20:]
               # print("%s" % (" ".join(self.feature_names[top10])))
            print()


        print("classification report:")
        print(metrics.classification_report(self.y_test, pred, target_names=['class 0','class 1']))


        print("confusion matrix:")
        print(metrics.confusion_matrix(self.y_test, pred))

        print()
        clf_descr = str(clf).split('(')[0]
        return clf_descr, f1_score, acc_score, precision_score, recall_score, train_time, \
                test_time, pred

    def show_most_informative_features(self, lst, n=20):
	"""
	Show most informative n features
	@param n: number of top features you want to show
	"""
        c_f = sorted(zip(lst, self.feature_names))
        top = zip(c_f[:n], c_f[:-(n+1):-1])
        #weights and feature names
        for (c1,f1),(c2,f2) in top:
            print "\t%.4f\t%-15s\t\t%.4f\t%-15s" % (c1,f1,c2,f2)

    def runTopClassifiers(self):
        '''Top determined by running all classifiers on dataset of size 20'''
        results=[]
        for clf, name in (
                #(SGDClassifier(alpha=.0001, n_iter=50, penalty="l2"),"SGD with Elastic-Net penalty"),
                (Perceptron(n_iter=50), "Perceptron"),
                (PassiveAggressiveClassifier(n_iter=50), "Passive-Aggressive")):#, (RidgeClassifier(tol=1e-2, solver="lsqr"), "Ridge Classifier"),(KNeighborsClassifier(n_neighbors=10), "kNN")
            print('=' * 80)
            print(name)
            results.append(self.benchmark(clf))

    # run all classifiers
    def runAllClassifiers(self):
        results = []
        for clf, name in (
                #(svm.SVC(cache_size = 500, class_weight='auto', kernel='rbf'),'SVM rbf'),
                #(svm.SVC(cache_size = 500, class_weight='auto', kernel='poly'),'SVM poly'),
                (SGDClassifier(alpha=.0001, n_iter=50, penalty="l2"),"SGD with l2 penalty"),
                (Perceptron(n_iter=50), "Perceptron"),
                #(KNeighborsClassifier(n_neighbors=10), "k Nearest Neighbors 10"),
                #(RidgeClassifier(tol=1e-2, solver="lsqr"), "Ridge Classifier"),
                (PassiveAggressiveClassifier(n_iter=50), "Passive-Aggressive"),
                (NearestCentroid(),"NearestCentroid"),
                #(MultinomialNB(alpha=.01), "Multinomial Naive Bayes - alpha .01"),
                (MultinomialNB(alpha=.05), "Multinomial Naive Bayes"),
                #(MultinomialNB(alpha=.1), "Multinomial Naive Bayes - alpha .1"),
                #(MultinomialNB(alpha=.5), "Multinomial Naive Bayes - alpha .5"),
                #(MultinomialNB(alpha=1), "Multinomial Naive Bayes - alpha 1"),
                (BernoulliNB(alpha=.01), "Bernouli Naive Bayes"),
                #(GaussianNB(),"Gaussian Naive Bayes"), # doesn't handle sparse matrices
                (DummyClassifier(), "Dummy Baseline")
                ):
            print('=' * 80)
            print(name)
            results.append(self.benchmark(clf))

        #for penalty in ["l2", "l1"]:
            #print('=' * 80)
            #print("%s penalty" % penalty.upper())
            # Train Liblinear model
            #results.append(self.benchmark(LinearSVC(loss='l2', penalty=penalty,
              #                                      dual=False, tol=1e-3)))

            # Train SGD model
            #results.append(self.benchmark(SGDClassifier(alpha=.0001, n_iter=50,
             #                                      penalty=penalty)))

        # Train SGD with Elastic Net penalty
        #print('=' * 80)
        #print("Elastic-Net penalty")
        #results.append(self.benchmark(SGDClassifier(alpha=.0001, n_iter=50,
         #                                      penalty="elasticnet")))

        #Train NearestCentroid without threshold
        '''
        print('=' * 80)
        print("NearestCentroid (aka Rocchio classifier)")
        results.append(self.benchmark(NearestCentroid()))
        '''

        # Train sparse Naive Bayes classifiers
        '''
        print('=' * 80)
        print("Naive Bayes")
        results.append(self.benchmark(MultinomialNB(alpha=.01)))
        results.append(self.benchmark(BernoulliNB(alpha=.01)))
        '''


        #class L1LinearSVC(LinearSVC):

#            def fit(self, X, y):
 #               # The smaller C, the stronger the regularization.
  #              # The more regularization, the more sparsity.
   #             self.transformer_ = LinearSVC(penalty="l1",
    #                                          dual=False, tol=1e-3)
     #           X = self.transformer_.fit_transform(X, y)
      #          return LinearSVC.fit(self, X, y)
#
 #           def predict(self, X):
  #              X = self.transformer_.transform(X)
   #             return LinearSVC.predict(self, X)

        #print('=' * 80)
        #print("LinearSVC with L1-based feature selection")
        #esults.append(self.benchmark(L1LinearSVC()))
        return results

   
    def drawDiagram(self, results):
	"""
	make basic bar diagram to compare classifier performance.
        @param results: the benchmark results on all classifiers
	"""
        indices = np.arange(len(results))

        results = [[x[i] for x in results] for i in range(7)]

        clf_names, f1_score, acc_score, precision_score, recall_score, training_time, test_time = results
        training_time = np.array(training_time) / np.max(training_time)
        test_time = np.array(test_time) / np.max(test_time)

        pl.figure(figsize=(12,8))
        pl.title("Score")
        pl.barh(indices, f1_score, .2, label="f1", color='r')
        pl.barh(indices+.3, acc_score, .2, label='accuracy', color='y')
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


                

    
    def corpusFromDB(self, doc_num):
	"""
	Build corpus from data in DB
        @param doc_num: the number of docs you are gonna use
	"""
        db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation')
        c=db.cursor()
        # we only want documents that have at least three valid annotations
        c.execute("SELECT  doc_id, doc_html, sum(valid) as tot_valid FROM Documents natural join Annotations WHERE doc_id > 1 group by doc_id having tot_valid >= 3 order by doc_id desc LIMIT %s "%(doc_num,))#a_id > 125")
        #c.execute("select doc_id, doc_html from Documents where doc_id > 1 order by doc_id desc LIMIT %s"%(doc_num,))
        
        rowall=c.fetchall()
        for row in rowall:
          
            doc=nltk.clean_html(row[1])
            text=nltk.Text([self.preprocessEachWord(w) for w in nltk.wordpunct_tokenize(doc) if len(w) >= 1 and not all(a in string.punctuation for a in w)])
            self.texts[int(row[0])]=text
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
        
        return self.tfidf_bins[document].get(word, 8) # use this so punct get the max tfidf bin



    
    def extractDependency(self,text, doc_id):
	"""
	Extract information of a text using stanford corenlp
        @param text: the input text
        @param doc_id: The ID of the document for this text.
	"""
        print "dependency extraction"
        
        sents=nltk.sent_tokenize(text)
        
        currTotal=0
        sent_index = 0
        
        # check to see if we've parsed this document or not
        parse_this = not doc_id in self.coreParsed
        if parse_this:
            print "Parsing..."
        else:
            print "Parse already in cache."

        for sent in sents:
            if parse_this:
                result=self.server.parse(sent)
                #pprint(result)
                newlsts=(loads(result))['sentences']
                # only parse this sentence if we haven't already
                if doc_id not in self.coreParsed:
                    self.coreParsed[doc_id]=newlsts
                else:
                    self.coreParsed[doc_id].extend(newlsts)
            #pprint(newlsts)
            #sent_len=int(newlsts[-1]['words'][-1][1]['CharacterOffsetEnd'])
            sent_len = \
                    int(self.coreParsed[doc_id][sent_index]['words'][-1][1]['CharacterOffsetEnd'])

            self.offsets.extend([currTotal for k in 
                    range(len(self.coreParsed[doc_id][sent_index]))])

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
            fnames.extend(["token", "token: -1",  'token +1', "token: -2", 'token +2', 'lemma', 
                    'lemma: -1', 'lemma: +1', 'lemma: -2', 'lemma: +2'])
            
            features['token'] = tokens[index]
            self.plus_minus_features_list('token', 1, tokens, index, features)
            self.plus_minus_features_list('token', 2, tokens, index, features)
            
            features['lemma'] = lemmas[index]
            self.plus_minus_features_list('lemma', 1, lemmas, index, features)
            self.plus_minus_features_list('lemma', 2, lemmas, index, features)
            
            fnames.extend(['bigram -1', 'bigram +1', 'trigram -1', 'trigram 0', 'trigram +1'])
            
            # bigrams
            # ignore bigrams that include stopwords, punctuation, and numbers
            if index > 0:
                if self.filter_word(lemmas[index-1]):
                    features['bigram -1'] = 'null'
                else:
                    features['bigram -1'] = lemmas[index-1] + ' ' + lemmas[index]
            else:
                features['bigram -1'] = 'null'
            if index < len(lemmas) - 1:
                if self.filter_word(lemmas[index+1]):
                    features['bigram -1'] = 'null'
                else:
                    features['bigram +1'] = lemmas[index] + ' ' + lemmas[index+1]
            else:
                features['bigram +1'] = 'null'
            
            # trigrams
            # ignore trigrams that include stopwords, punctuation, and numbers
            if index > 1:
                if self.filter_word(lemmas[index-2]) or self.filter_word(lemmas[index-1]):
                    features['trigram - 1'] = 'null'
                else:
                    features['trigram - 1'] = lemmas[index - 2] + ' ' + lemmas[index - 1] \
                            + lemmas[index]
            else:
                features['trigram - 1'] = 'null'
            if index > 0 and index < len(lemmas) - 1:
                if self.filter_word(lemmas[index-1]) or self.filter_word(lemmas[index+1]):
                    features['trigram 0'] = 'null'
                else:
                    features['trigram 0'] = lemmas[index - 1] + ' ' + lemmas[index] + ' ' + \
                            lemmas[index + 1]
            else:
                features['trigram 0'] = 'null'
            if index < len(lemmas) - 2:
                if self.filter_word(lemmas[index+1]) or self.filter_word(lemmas[index+2]):
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
            self.plus_minus_features_list('pos', 1, poses, index, features)
            self.plus_minus_features_list('pos', 2, poses, index, features)

        if feat_entity:
            # use the type of named entity as a feature
            fnames.extend(['entity type', 'entity bigram - 1', 'entity bigram + 1', 
                    'entity trigram - 1', 'entity trigram 0', 'entity trigram + 1'])
            features['entity type'] = entities[index]
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
            features['InTitle'] = int(stems[index] in self.title_words)
        
        if feat_TFIDF:
            # use TFIDF as a feature
            fnames.extend(['TFIDF'])
            features['TFDIF']=self.TFIDF(stems[index],self.texts[self.docID])
        
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
            else:
                features['descriptiveness average'] = 'null'
            for i in range(1,3):
                features.pop("descriptiveness: -%d" % i)
                features.pop("descriptiveness: +%d" % i)
            
        
        if feat_word_lists:
            # use the special lists of words (factives, implicatives, etc.)
            for known_set in self.doc_sets.keys():
                fnames.append(known_set)
                
                features[(known_set)] = stems[index] in self.doc_sets[known_set]
                self.plus_minus_features_dict(known_set, 1, stems, self.doc_sets[known_set],
                        index, features)
                self.plus_minus_features_dict(known_set, 2, stems, self.doc_sets[known_set],
                        index, features)
                features[known_set + " in context"] = features[known_set + ": +1"] or \
                        features[known_set + ": -1"] or features[known_set + ": +2"] or \
                        features[known_set + ": -2"]
                for i in range(1,3):
                    features.pop(known_set + ": -%d" % i)
                    features.pop(known_set + ": +%d" % i)

        return features
    
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
                if self.filter_word(values_list[index - offset]):
                    features[fname + ": -%d" % offset] = 'null'
                else:
                    features[fname + ": -%d" % offset] = values_list[index - offset]
            else:
                features[fname + ": -%d" % offset] = values_list[index - offset]
        else:
            features[fname + ": -%d" % offset] = 'null'
            
        if index < len(values_list) - offset:
            if filter:
                if self.filter_word(values_list[index + offset]):
                    features[fname + ": +%d" % offset] = 'null'
                else:
                    features[fname + ": +%d" % offset] = values_list[index + offset]
            else:
                features[fname + ": +%d" % offset] = values_list[index + offset]
        else:
            features[fname + ": +%d" % offset] = 'null'
    
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
    
    def filter_word(self, word):
        """
        Return true if this words meets any of the criteria for filtering (stopword, punctuation,
        numeric, etc.).
        @param word: The word to be checked.
        @return: True if the word should be filtered out, False if the word should be included.
        """
        
        return (
                # stopwords
                word in nltk.corpus.stopwords.words('english') or 
                # punctuation and numbers
                all(a in string.punctuation or unicode.isnumeric(a) for a in word) or 
                # "words" that begin with punctuation
                unicodedata.category(word[0])[0] == 'P' or 
                # "words" that begin with symbols
                unicodedata.category(word[0])[0] == 'S' or 
                # "words" that begin with numbers
                unicodedata.category(word[0])[0] == 'N' or 
                # short words
                len(word) < 3
        )
    
    def isHighlighted(self,cstart,cend, i):
	"""
	Return whether a word is highlighted
    	@param cstart: the offset of the first char in the word
	@param cend: the offset of the last char in the word
	@param i: the annotation index of the word
	"""
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
        
                
            
    
    def generate_feature_datasets(self):
	"""
	Generate feature vectors and labels for all the words in the corpus
	"""

        invalid_ann={52:[225,224], 104:[224, 225], 148:[225,224],146:[224, 225],118:[167,153], 174:[167,153],68: [167],166:[167,153],39:[167,153]}

        train_set=[]
        targets=[]
        doc_offsets={}
        
        # for recoding average annotations into target classes for training
        recode_dict = {0:0, 1:0, 2:1, 3:1, 4:1, 5:1}

        
        f_counter=0
        for doc_id in self.texts.keys():
            print "Start Processing document: %d"%doc_id
            self.docID=doc_id
            doc_offsets[doc_id]=[f_counter,0]
            self.offsets=[]
            #self.coreParsed=[]
            
            db=MySQLdb.connect(host='eltanin.cis.cornell.edu', user='annotator',passwd='Ann0tateTh!s', db='FrameAnnotation', charset='ascii')
            c=db.cursor()
            #c.execute('set charset utf8')
           
            c.execute("SELECT doc_html from Documents WHERE doc_id = %s"%(doc_id,))
           
            text=nltk.clean_html(c.fetchone()[0])
            separate=text.split('\n',1)
            self.title_words=[self.stemmer.stem(self.lemmer.lemmatize(w)) for w in nltk.wordpunct_tokenize(separate[0])]
            
            self.extractDependency(text, doc_id)
            
            c.execute('SELECT char_annotation, a_id from Annotations WHERE doc_id = %s and valid = 1'%(doc_id,))
            #c.execute('SELECT char_annotation, a_id from Annotations WHERE doc_id = %s'%(doc_id,))
            rows=c.fetchall()

            num_ann=len(rows)
            self.start_indices=[]
            self.end_indices=[]

            for i in range(num_ann):
                indexStr=rows[i][0]

                if indexStr is None or (rm_invdata and doc_id in invalid_ann and rows[i][1] in invalid_ann[doc_id]):
                    print 'invalid annotation %d %d ignored'%(doc_id, rows[i][1])
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
            for i in range(len(self.coreParsed[doc_id])):
                    #sent=self.coreParsed[doc_id][i]['text']
                tuples=self.coreParsed[doc_id][i]['dependencies']
                    #pprint(tuples)
                words=self.coreParsed[doc_id][i]['words'] #words are words properties
                for windex in range(len(words)):
                    
                    #ignore punctuations
                    if self.filter_word(words[windex][0]):
                        continue
                    f1=self.generateFeatures(windex,words)
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
                    # recode annotations. 0-1 annotators = low, 2-3 = medium, 4-5 = high
                    ation_aggregate = 0
                    for a in range(len(self.start_indices)):
                        #train_set.append(f1)
                        #pprint(f1)
                        ation_aggregate += \
                                self.isHighlighted(int(words[windex][1]['CharacterOffsetBegin']) +\
                                self.offsets[i], int(words[windex][1]['CharacterOffsetEnd']) + \
                                self.offsets[i], a)
                        '''
                        targets.append(
                                self.isHighlighted(int(words[windex][1]['CharacterOffsetBegin']) + 
                                self.offsets[i], int(words[windex][1]['CharacterOffsetEnd']) + 
                                self.offsets[i], a)
                                )
                        f_counter+=1
                        '''
                    train_set.append(f1)
                    # targets.append(recode_dict[ation_aggregate])
                    normed_ation = float(ation_aggregate) / len(self.start_indices)
                    if normed_ation >= float(1/3.0):
                        targets.append(1)
                    else:
                        targets.append(0)
                    # what percentage of annotators highlighted this word?
                    '''
                    if normed_ation == 0:
                        # no one highlighted, this is not framed
                        targets.append(0)
                    elif normed_ation <= float(1/3.0):
                        # less than half the annotators highlighted, low likelihood
                        targets.append(1)
                    else:
                        # more than half the annotators highlighted, high likelihood
                        targets.append(2)
                    '''
                    f_counter+=1

            doc_offsets[doc_id][1]=f_counter
        return (train_set,targets, doc_offsets)
    
    def loadParses(self, parses_file):
        """
        Load parsed versions of documents from a file.
        """
        
        print "Loading parses from %s..." % parses_file
        try:
            self.coreParsed = cPickle.load(open(parses_file, 'r'))
        except:
            # the file doesn't exist yet. do the parses and save them to this file.
            self.coreParsed = {}

def saveModel(classifier, type='nb'):
    """
    Save the trained model in python pickle module
    @param type: the type of the classifier you are saving
    """

    f = open(type+'_classifier.pickle', 'wb')
    pickle.dump(classifier, f)
    f.close()

def loadModel(type='nb'):
    """
    load the saved model
    @param type: the type of the classifier you are loading
    """
    f = open(type+'_classifier.pickle')
    model=pickle.load(f)
    f.close()
    return model

def main(argv=None):
    print "Start Feature Extractor"
    # Preprocess read file
    num_doc='50' # number of documents used in training set
    parses_file = None # by default, parse it yourself
    if sys.argv != None:
        num_doc=str(sys.argv[1])
        print 'set num to %s'%num_doc
    if len(sys.argv) > 2:
        parses_file = str(sys.argv[2])
    #execute
    extractor=FeatureExtractor()
    extractor.prepareExtractor(num_doc)
    if parses_file:
        extractor.loadParses(parses_file)
    extractor.executeExtractor(parses_file)

    
        
    
    
if __name__ == "__main__":
    main() 

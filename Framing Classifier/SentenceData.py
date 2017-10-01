# Timothy Berrill
# Sentence Data should be able to load in the saved pickle Annotated Articles and do all of the necessary data
# edits and shuffling necessary before feature extraction. Might also expand this to include feature extraction
# eventually if I feel like it.

# ---------------------------- Imports ----------------------------
from sklearn.feature_extraction import DictVectorizer
from sklearn import svm
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.dummy import DummyClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn import metrics
from sklearn.pipeline import Pipeline
import Clean_Process_Frames
from Clean_Process_Frames import *
from nltk import word_tokenize
from nltk.corpus import stopwords
import numpy
import csv


# ---------------------------- Functions ----------------------------

# Method used for printing out the performance metrics of different classifiers
# This takes advantage of the sklearn metrics classification report method. There
# used to be a lot more here but now its basically a wrapper method for the sklearn one...
def score_individual_frames(test_array, classifier):
    predicted = classifier.predict(test_array)
    print(str(metrics.classification_report(y_array_test, predicted)))
    print("\n\n\n")
    return


# Prints out different framing predictions for sentences
def predict_print(X_array_test, classifier, y_array_test):
    predicted = classifier.predict(X_array_test)
    count1 = 0
    x = 0
    for x in range(len(predicted)):
        count = 0
        print(X_array[count1])
        is_found_p = False
        is_found_a = False
        framelist = []
        for y in range(len(predicted[x])):
            index = (list(mlb.classes_))[count]
            index2 = index - (index % 3)
            if not index2 in framelist:
                if predicted[x][y] == 1 and y_array_test[x][y] == 1:
                    is_found_p = True
                    print(Colors.GREEN + str(index_dictionary.get(index2)) + Colors.RESET)
                    framelist.append(index2)
                elif y_array_test[x][y] == 1:
                    is_found_a = True
                    print(Colors.RED + str(index_dictionary.get(index2)) + Colors.RESET)
                    framelist.append(index2)
                elif predicted[x][y] == 1:
                    is_found_p = True
                    print(Colors.BLUE + str(index_dictionary.get(index2)) + Colors.RESET)
                    framelist.append(index2)
            count += 1
        framelist.clear()
        if not is_found_p and not is_found_a:
            print(Colors.GREEN + "No Frame" + Colors.RESET)

        print("\n")
        count1 += 1
        return


# Converts individual words to features by creating unique integer identifiers
def convert_words_to_features(word, dictionary, index):

    #Check if the word already exists in the word dictionary
    if word not in dictionary:
        #if its not, add it to the dictionary and increase the code index
        dictionary[word] = str(index[0])
        index[0] += 1
    #return the index of the word (added to the dictionary, or if already found)
    return dictionary[word]


# Converts individual bi-grams and tri-grams to features with unique integer identifiers
def convert_grams_to_features(words, dictionary, index):
    temp_string = ""

    # combine words together into longer string
    for x in words:
        temp_string += x + " "
    # Check if they exist in the dictionary
    if temp_string not in dictionary:
        # If not, add it to the dictionary and increase the code index
        dictionary[temp_string] = str(index[0])
        index[0] += 1
    # Return the index of the n-gram
    return dictionary[temp_string]


# Converts words to features
def handle_non_numerical_data(array):
    x1 = 0
    for word_list in array:

        def convert_to_int(val):
            return text_digit_vals[val]

        unique_elements = set(word_list)
        for unique in unique_elements:
            if unique not in text_digit_vals:
                text_digit_vals[unique] = x1
                x1 += 1

        index = 0
        for word in word_list:
            word_list[index] = convert_to_int(word)
            index += 1
    return numpy.asarray(array, dtype=object)


# Voting Classifier takes a test array, the voting array and a classifiers and lets the
# Classifier vote on the frames. I think this will eventually be the best method
def vote_on_frames(array_test, vote_array, classifier, weight):
    # initially predict the characteristics of the test array
    predicted = classifier.predict(array_test)
    predicted2 = ""
    try:
        predicted2 = classifier.predict_proba(array_test)
    except AttributeError:
        i = 0
    # print(predicted2)
    # Loop through the classifier's predictions
    for x in range(len(predicted)):
        count = 0
        # check each frame for each sentence
        for y in range(len(predicted[x])):
            # If the frame was predicted by the classifier
            if predicted[x][y] == 1:
                # Add to the vote array the weight of the classifier
                vote_array[x][y] += (weight)
            count += 1

    return


# Voting classifier prints out the voting classifier predictions alongside the actual annotations
def voting_classifier_new(vote_array, sentences, threshold, verbose):
    count1 = 0

    # Loop through the voting array
    for x in range(len(vote_array)):
        count = 0
        if verbose:
            # Print out the sentences if in verbose mode
            print(sentences[count1])
        is_found_p = False
        # Loop through potential frames
        for y in range(15):
            # If the total votes are greater than the voting threshold
            if vote_array[x][y] >= threshold:
                is_found_p = True
                if verbose:
                    # Print the frames present in the sentence
                    print(Colors.GREEN + str(index_dictionary.get(y)) +
                          " " + str(vote_array[x][y]) + Colors.RESET)
            count += 1
        if not is_found_p and verbose:
            # If no frames are present, print no frame
            print(Colors.GREEN + "No Frame" + Colors.RESET)
        if verbose:
            print("\n\n")
        count1 += 1
    return


# Voting classifier prints out the voting classifier predictions alongside the actual annotations
def voting_classifier(vote_array, y_array_test, threshold, verbose):
    wrong_with_0 = 0
    wrong_with_50 = 0
    count1 = 0
    correct = 0
    guessed = 0
    total = 0
    count1 = 0
    # Loop through the voting array
    for x in range(len(vote_array)):
        count = 0
        if verbose:
            # Print the sentence text
            print(X_array[count1])
        is_found_p = False
        is_found_a = False
        # Loop through potential frames
        for y in range(15):
            # If the vote is higher than the threshold, and the frame is actually present
            # True positive
            if vote_array[x][y] >= threshold and y_array_test[x][y] == 1:
                is_found_p = True
                total += 1
                correct += 1
                if verbose:
                    # print the frame in green followed by the vote score
                    print(Colors.GREEN + str(index_dictionary.get(y)) +
                          " " + str(vote_array[x][y]) + Colors.RESET)
            # If the vote is not higher than the threshold, but the frame is actually present
            # False negative
            elif y_array_test[x][y] == 1:
                total += 1
                count1 += 1
                is_found_a = True
                if verbose:
                    # Print the frame in red
                    print(Colors.RED + str(index_dictionary.get(y)) +
                          " " + str(vote_array[x][y]) + Colors.RESET)
                if vote_array[x][y] == 0:
                    wrong_with_0 += 1
                elif vote_array[x][y] >= threshold / 2:
                    wrong_with_50 += 1
            # If the vote is higher than the threshold but not annotated
            # False positive
            elif vote_array[x][y] >= threshold:
                guessed += 1
                count1 += 1
                is_found_p = True
                if verbose:
                    # Print the frame in blue
                    print(Colors.BLUE + str(index_dictionary.get(y)) +
                          " " + str(vote_array[x][y]) + Colors.RESET)
            count += 1

        # If no frame was found in both annotations and votes
        if not is_found_p and not is_found_a:
            if verbose:
                # Print no frame in green (Overall true negative)
                print(Colors.GREEN + "No Frame" + Colors.RESET)

        if verbose:
            print("\n\n")
        count1 += 1

    # Calculate recall score
    recall = float(correct) / total
    # Calculate percision score
    precision = float(correct) / (guessed + correct)
    # Calculate f1-score
    f_score = (2 * precision * recall) / (precision + recall)
    # Print the results
    print ("Correctly identified " + str(correct) + " out of " + str(total))
    print("Precision : " + str(round(precision, 4)))
    print("Recall : " + str(round(recall, 4)))
    print("F score: " + str(round(f_score, 4)))
    print("Wrong with 0 votes: " + str(wrong_with_0))
    print("Wrong with 50% of threshold vote: " + str(wrong_with_50))
    print("\n\n")
    return f_score


# ---------------------------- Main ----------------------------

# Dictionary for recording word values as integers
text_digit_vals = {}
# Python code that processes the json files
Clean_Process_Frames.main(False)
# Loads processed annotations from pickle
all_annotations = pickle.load(open("annotations.p", "rb"))
# List of stopwords and punctuation
stop = set(stopwords.words('english'))
stop.update(['.', ',', '$', "''", '``', '"',
             "'", '?', '!', ':', ';', '(', ')',
             '[', ']', '{', '}', '--', 'n\'t', '-',
             'primary', '\'s'])
tagset = {"$": 0, "''": 1, "(": 2, ")": 3, ",": 4, "--": 5, ".": 6,
          ":": 7, "CC": 8, "CD": 9, "DT": 10, "EX": 11, "FW": 12,
          "IN": 13, "JJ": 14, "JJR": 15, "JJS": 16, "LS": 17, "MD": 18,
          "NN": 19, "NNP": 20, "NNPS": 21, "NNS": 22, "PDT": 23, "POS": 24,
          "PRP": 25, "RB": 26, "RBR": 27, "RBS": 28, "RP": 29, "SYM": 30,
          "TO": 31, "UH": 32, "VB": 33, "VBD": 34, "VBG": 35, "VBN": 36,
          "VBP": 37, "VBZ": 38, "WDT": 39, "WP": 40, "WP$": 41, "WRB": 42, "\"": 43}
# Open imagery ratings file for vividness scores, store in vivid dictionary
f = open("ImageryRatings.csv", "r")
reader = csv.reader(f)
vivid_dict = {rows[0].lower(): rows[1] for rows in reader}
f.close()

# Concrete dictionary is for scoring concrete / abstract scores
concrete_dict = {}
error_num = 0
valid_num = 0
# Open the abstract/concrete file and store values in the dictionary
with open("abstract-concrete.txt", "r") as f:
    for line in f:
        try:
            (val, key) = line.split()
            concrete_dict[key] = val
            valid_num += 1
        except ValueError:
            error_num += 1
f.close()

mlb = MultiLabelBinarizer()
count = 0
frame_array = []
X_array = []
other_X_array = []

# Dictionary array is an array of feature dictionaries which contain the features and scores for each of them
dict_array = []
# Word dictionary will be used to create unique word listings like {"the" : 403} ect...
word_dictionary = {}
# Word index will increase with every unique word
word_index = [0]

# Bi-gram dictionary will be used to create unique bi-gram listings like {"the car" : 345} ect...
bi_gram_dictionary = {}
# Bi_gram_index will increase with every unique bi-gram
bi_gram_index = [0]

# Tri_gram dictionary will be used to create unique tri-gram listings ike {"the car was" : 2435} ect...
tri_gram_dictionary = {}
# Tri_gram_index will increase with every unique tri-gram
tri_gram_index = [0]

current_sentence_count = 0

# Attempt to load all pre-processing information, this will make things much faster if nothing
# in the data set changes.
try:
    dict_array = pickle.load(open("feature_dict_array.p", "rb"))
    X_array = pickle.load(open("X_array.p", "rb"))
    other_X_array = pickle.load(open("other_X_array.p", "rb"))
    frame_array = pickle.load(open("frame_array.p", "rb"))
    print("Feature dictionaries loaded from pickle.")

# If pickle can't load everything, it needs to be reprocessed
except FileNotFoundError:
    # Clear anything that might have successfully loaded from pickle
    dict_array.clear()
    X_array.clear()
    other_X_array.clear()
    frame_array.clear()
    print("No Feature dictionaries loaded, processing sentences...")

    frame_test = []
    # Loop through the annotation objects
    for x in range(3):
        for article in all_annotations[x][1]:
            # Loop through sentences within articles
            for sentence in article.sentences:
                one_gram = [] # for storing uni grams
                two_gram = [] # for storing bi grams
                three_gram = [] # for storing tri grams
                sentence.pos_process() # do part of speech processing on sentences
                sentence.ne_process() # do named entity processing on sentences
                sentence.create_n_grams(one_gram, two_gram, three_gram) # create grams
                taglist = [0 for x in range(43)]
                text_pos = sentence.text_pos

                # If the sentence is not the PRIMARY tag do the rest of the processing
                if not (sentence.text == "PRIMARY"):
                    current_sentence_count += 1
                    temp_feature_dict = {}

                    # Create a word list using the nltk word tokenizer
                    words = word_tokenize(sentence.text)
                    # remove stop words and punctuation and such
                    words = [i for i in words if i.lower() not in stop]

                    # Temporary feature dictionary will be created for each sentence
                    # Extracted features will get added to this
                    temp_feature_dict = {}

                    # Length Feature (currently inactive)
                    # temp_feature_dict["length"] = len(sentence.text)

                    # is First feature

                    # if sentence.position < 3:
                    #     temp_feature_dict["is_first"] = 1
                    # else:
                    #     temp_feature_dict["is_first"] = 0


                    # POS features (counts and pairs)
                    last = ""
                    for x in text_pos:
                        tagged = tagset.get(x[1])
                        if last != "":
                            feature = str(last) + "_" + str(tagged)
                            if feature in temp_feature_dict:
                                temp_feature_dict[feature] = temp_feature_dict[feature] + 1
                            else:
                                temp_feature_dict[feature] = 1

                        last = tagged
                        taglist[tagged] += 1
                    # temp_feature_dict["pos_tag_count"] = taglist


                    # Create word features and score vividness
                    vivid_score = 0
                    average_concrete = 0
                    highest_concrete = 0
                    highest_abstract = 0
                    for x in words:
                        if x.lower() in vivid_dict:
                            vivid_score += float(vivid_dict.get(x.lower()))
                        if x.lower() in concrete_dict:
                            average_concrete += float(concrete_dict.get(x.lower()))
                            if float(concrete_dict.get(x.lower())) > highest_concrete:
                                highest_concrete = float(concrete_dict.get(x.lower()))
                            if float(concrete_dict.get(x.lower())) < highest_abstract:
                                highest_abstract = float(concrete_dict.get(x.lower()))
                        temp_string = "1gram_"
                        temp_string += convert_words_to_features(x, word_dictionary, word_index)
                        temp_feature_dict[temp_string] = 1

                    # temp_feature_dict["highest_concrete"] = highest_concrete
                    # temp_feature_dict["highest_abstract"] = highest_abstract
                    if len(words) > 0:
                        vivid_score = vivid_score / len(words)
                        average_concrete = average_concrete / len(words)
                    else:
                        vivid_score = 0

                    # temp_feature_dict["vivid_score"] = vivid_score
                    # temp_feature_dict["average_concrete_score"] = average_concrete

                    # Create bi-gram features
                    for x in two_gram:
                        temp_string = "2gram_"
                        temp_string += convert_grams_to_features(x, bi_gram_dictionary, bi_gram_index)
                        temp_feature_dict[temp_string] = 1
                        #TODO insert code here to check for figurativeness and record highest score in sentence


                    # Create tri-gram features
                    for x in three_gram:
                        temp_string = "3gram_"
                        temp_string += convert_grams_to_features(x, tri_gram_dictionary, tri_gram_index)
                        # temp_feature_dict[temp_string] = 1

                    # Named Entity
                    # if sentence.is_ne_present:
                    #     temp_feature_dict["is_ne_present"] = 1
                    # else:
                    #     temp_feature_dict["is_ne_present"] = 0

                    # Sentiment analysis feature
                    vs = sentence.sentiment_process()
                    # temp_feature_dict["sentiment_score"] = math.fabs(vs.get('compound'))
                    # temp_feature_dict["sentiment_pos"] = math.fabs(vs.get('pos'))
                    # temp_feature_dict["sentiment_neg"] = math.fabs(vs.get('neg'))
                    # temp_feature_dict["sentiment_neu"] = math.fabs(vs.gets('neu'))



                    dict_array.append(temp_feature_dict)

                    other_X_array.append(words)
                    X_array.append(sentence.text)
                    frame_array.append(sentence.simple_codes)


                    for x in sentence.simple_codes:
                        if x not in frame_test:
                            print(x)
                            frame_test.append(x)

                    if current_sentence_count % 1000 == 0:
                        print("Processed " + str(current_sentence_count) + " sentences")

    pickle.dump(dict_array, open("feature_dict_array.p", "wb"))
    pickle.dump(other_X_array, open("other_X_array.p", "wb"))
    pickle.dump(X_array, open("X_array.p", "wb"))
    pickle.dump(frame_array, open("frame_array.p", "wb"))
    print("Done with sentence processing.")


with open('codes.json') as code_file:
    codes = json.load(code_file, encoding="utf-8")
code_dictionary = {}
index_dictionary = {}
for x, key in enumerate(codes.keys()):
    if count % 3 == 0 and count / 3 < 15:
        index_dictionary[(x / 3)] = str(codes.get(key))

    code_dictionary[str(key)] = str(codes.get(key))
    count += 1
count = 0

print(index_dictionary)

X_array_all = numpy.asarray(X_array, dtype=object)
other_X_array = numpy.asarray(other_X_array, dtype=object)


y_array_all = mlb.fit_transform(frame_array)
print(mlb.classes_)


X_array_train = X_array_all[int(len(X_array_all)*.005):]
X_array_test = X_array_all[:int(len(y_array_all)*.005)]
y_array_test = y_array_all[:int(len(y_array_all)*.005)]
print("Testing " + str(len(X_array_test)) + " sentences")


other_X_array = (handle_non_numerical_data(other_X_array))
other_X_array = mlb.fit_transform(other_X_array)


other_X_array_train = other_X_array[int(len(other_X_array)*.005):]
y_array_train = y_array_all[int(len(y_array_all)*.005):]

other_X_array_test = other_X_array[:int(len(other_X_array)*.005)]


vectorizer = DictVectorizer(sparse=True)
X_dict_array = vectorizer.fit_transform(dict_array)
X_dict_array_train = X_dict_array[int(len(X_array_all)*.005):]
X_dict_array_test = X_dict_array[:int(len(X_array_all)*.005)]

load_classifiers = [False,   # 0 TFIDF
                    True,    # 1 SVC
                    False,   # 2 SGD
                    False,   # 3 adam
                    True,    # 4 lbfgs
                    False,   # 5 TREE
                    False,   # 6 KN
                    False]   # 7 False


# TF-IDF Classifier
if load_classifiers[0]:
    try:
        tfidf_ovr_classifier = pickle.load(open("tfidf_ovr_classifier.p", "rb"))
        print("tfidf classifier Loaded.")

    except FileNotFoundError:
        print("tfidf Classifier not loaded, needs to be trained...")
        tfidf_ovr_classifier = Pipeline([
            ('vectorizer', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', OneVsRestClassifier(svm.LinearSVC(verbose=True)))])
        tfidf_ovr_classifier.fit(X_array_train, y_array_train)
        pickle.dump(tfidf_ovr_classifier, open("tfidf_ovr_classifier.p", "wb"))
        print("tfidf classifier Created.")


# One Vs Rest Classifier
if load_classifiers[1]:
    try:
        one_vs_rest_classifier = pickle.load(open("linear_svc_classifier.p", "rb"))
        print("LinearSVC Classifier Loaded.")

    except FileNotFoundError:
        print("LinearSVC Classifier not loaded, needs to be trained...")
        one_vs_rest_classifier = OneVsRestClassifier(svm.LinearSVC(verbose=True))
        one_vs_rest_classifier.fit(X_dict_array_train, y_array_train)
        pickle.dump(one_vs_rest_classifier, open("linear_svc_classifier.p", "wb"))
        print("Linear SVC Classifier Created.")


# Neural Network MLP SGD Classifier
if load_classifiers[4]:
    try:
        mlp_sgd_classifier = pickle.load(open("mlp_sgd_classifier.p", "rb"))
        print("MLP SGD Classifier Loaded.")

    except EOFError:
        print("MLP SGD end of file error.")

    except FileNotFoundError:
        print("MLP SGD Classifier not loaded, needs to be trained...")
        mlp_sgd_classifier = MLPClassifier(hidden_layer_sizes=10, verbose=True, max_iter=150, solver='sgd')
        mlp_sgd_classifier.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_sgd_classifier, open("mlp_sgd_classifier.p", 'wb'))
        print("MLP SGD Classifier Created.")


# Neural Network MLP SGD 2 Classifier
if load_classifiers[7]:
    try:
        mlp_sgd_classifier2 = pickle.load(open("mlp_sgd_classifier2.p", "rb"))
        print("MLP SGD 2 Classifier Loaded.")

    except EOFError:
        print("MLP SGD 2 end of file error.")

    except FileNotFoundError:
        print("MLP SGD 2 Classifier not loaded, needs to be trained...")
        mlp_sgd_classifier2 = MLPClassifier(hidden_layer_sizes=11, max_iter=150, verbose=True, solver='sgd')
        mlp_sgd_classifier2.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_sgd_classifier2, open("mlp_sgd_classifier2.p", 'wb'))
        print("MLP SGD 2 Classifier Created.")


# Neural Network MLP SGD 3 Classifier
if load_classifiers[2]:
    try:
        mlp_sgd_classifier3 = pickle.load(open("mlp_sgd_classifier3.p", "rb"))
        print("MLP SGD 3 Classifier Loaded.")

    except EOFError:
        print("MLP SGD 3 end of file error.")

    except FileNotFoundError:
        print("MLP SGD 3 Classifier not loaded, needs to be trained...")
        mlp_sgd_classifier3 = MLPClassifier(hidden_layer_sizes=25, verbose=True, max_iter=150, solver='sgd')
        mlp_sgd_classifier3.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_sgd_classifier3, open("mlp_sgd_classifier3.p", 'wb'))
        print("MLP SGD 3 Classifier Created.")


# Neural Network MLP SGD 4 Classifier
if load_classifiers[2]:
    try:
        mlp_sgd_classifier4 = pickle.load(open("mlp_sgd_classifier4.p", "rb"))
        print("MLP SGD 4 Classifier Loaded.")

    except EOFError:
        print("MLP SGD 4 end of file error.")

    except FileNotFoundError:
        print("MLP SGD 4 Classifier not loaded, needs to be trained...")
        mlp_sgd_classifier4 = MLPClassifier(hidden_layer_sizes=25, verbose=True, max_iter=150, solver='sgd')
        mlp_sgd_classifier4.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_sgd_classifier3, open("mlp_sgd_classifier4.p", 'wb'))
        print("MLP SGD 4 Classifier Created.")


# Neural Network MLP adam Classifier
if load_classifiers[4]:
    try:
        mlp_adam_classifier = pickle.load(open("mlp_adam_classifier.p", "rb"))
        print("MLP adam Classifier Loaded.")

    except EOFError:
        print("MLP adam end of file error.")

    except FileNotFoundError:
        print("MLP adam Classifier not loaded, needs to be trained...")
        mlp_adam_classifier = MLPClassifier(hidden_layer_sizes=15, verbose=True, max_iter=300, solver='adam')
        mlp_adam_classifier.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_adam_classifier, open("mlp_adam_classifier.p", 'wb'))
        print("MLP adam Classifier Created.")


# Neural Network MLP adam 2 Classifier
if load_classifiers[4]:
    try:
        mlp_adam_classifier2 = pickle.load(open("mlp_adam_classifier2.p", "rb"))
        print("MLP adam 2 Classifier Loaded.")

    except EOFError:
        print("MLP adam 2 end of file error.")

    except FileNotFoundError:
        print("MLP adam 2 Classifier not loaded, needs to be trained...")
        mlp_adam_classifier2 = MLPClassifier(hidden_layer_sizes=13, verbose=True, max_iter=100, solver='adam')
        mlp_adam_classifier2.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_adam_classifier2, open("mlp_adam_classifier2.p", 'wb'))
        print("MLP adam 2 Classifier Created.")


# Neural Network MLP adam 3 Classifier
if load_classifiers[4]:
    try:
        mlp_adam_classifier3 = pickle.load(open("mlp_adam_classifier3.p", "rb"))
        print("MLP adam 3 Classifier Loaded.")

    except EOFError:
        print("MLP adam 3 end of file error.")

    except FileNotFoundError:
        print("MLP adam 3 Classifier not loaded, needs to be trained...")
        mlp_adam_classifier3 = MLPClassifier(hidden_layer_sizes=19, verbose=True, max_iter=90, solver='adam')
        mlp_adam_classifier3.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_adam_classifier3, open("mlp_adam_classifier3.p", 'wb'))
        print("MLP adam 3 Classifier Created.")


# Neural Network MLP adam 4 Classifier
if load_classifiers[7]:
    try:
        mlp_adam_classifier4 = pickle.load(open("mlp_adam_classifier4.p", "rb"))
        print("MLP adam 4 Classifier Loaded.")

    except EOFError:
        print("MLP adam 4 end of file error.")

    except FileNotFoundError:
        print("MLP adam 4 Classifier not loaded, needs to be trained...")
        mlp_adam_classifier4 = MLPClassifier(hidden_layer_sizes=25, verbose=True, max_iter=90, solver='adam')
        mlp_adam_classifier4.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_adam_classifier4, open("mlp_adam_classifier4.p", 'wb'))
        print("MLP adam 4 Classifier Created.")


# Neural Network MLP adam 5 Classifier
if load_classifiers[7]:
    try:
        mlp_adam_classifier5 = pickle.load(open("mlp_adam_classifier5.p", "rb"))
        print("MLP adam 5 Classifier Loaded.")

    except EOFError:
        print("MLP adam 5 end of file error.")

    except FileNotFoundError:
        print("MLP adam 5 Classifier not loaded, needs to be trained...")
        mlp_adam_classifier5 = MLPClassifier(hidden_layer_sizes=25, verbose=True, max_iter=90, solver='adam')
        mlp_adam_classifier5.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_adam_classifier5, open("mlp_adam_classifier5.p", 'wb'))
        print("MLP adam 5 Classifier Created.")


# Neural Network MLP lbfgs Classifier
if load_classifiers[4]:
    try:
        mlp_lbfgs_classifier = pickle.load(open("mlp_lbfgs_classifier.p", "rb"))
        print("MLP lbfgs Classifier Loaded.")

    except EOFError:
        print("MLP lbfgs end of file error.")

    except FileNotFoundError:
        print("MLP lbfgs Classifier not loaded, needs to be trained...")
        mlp_lbfgs_classifier = MLPClassifier(hidden_layer_sizes=28, verbose=True, max_iter=500, solver='lbfgs')
        mlp_lbfgs_classifier.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_lbfgs_classifier, open("mlp_lbfgs_classifier.p", 'wb'))
        print("MLP lbfgs Classifier Created.")


# Neural Network MLP 2 lbfgs Classifier
if load_classifiers[4]:
    try:
        mlp_lbfgs_classifier2 = pickle.load(open("mlp_lbfgs_classifier2.p", "rb"))
        print("MLP lbfgs 2 Classifier Loaded.")

    except EOFError:
        print("MLP lbfgs 2 end of file error.")

    except FileNotFoundError:
        print("MLP lbfgs 2 Classifier not loaded, needs to be trained...")
        mlp_lbfgs_classifier2 = MLPClassifier(hidden_layer_sizes=32, verbose=True, max_iter=700, solver='lbfgs')
        mlp_lbfgs_classifier2.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_lbfgs_classifier2, open("mlp_lbfgs_classifier2.p", 'wb'))
        print("MLP lbfgs 2 Classifier Created.")


# Neural Network MLP 3 lbfgs Classifier
if load_classifiers[4]:
    try:
        mlp_lbfgs_classifier3 = pickle.load(open("mlp_lbfgs_classifier3.p", "rb"))
        print("MLP lbfgs 3 Classifier Loaded.")

    except EOFError:
        print("MLP lbfgs 3 end of file error.")

    except FileNotFoundError:
        print("MLP lbfgs 3 Classifier not loaded, needs to be trained...")
        mlp_lbfgs_classifier3 = MLPClassifier(hidden_layer_sizes=30, verbose=True, max_iter=500, solver='lbfgs')
        mlp_lbfgs_classifier3.fit(X_dict_array_train, y_array_train)
        pickle.dump(mlp_lbfgs_classifier3, open("mlp_lbfgs_classifier3.p", 'wb'))
        print("MLP lbfgs 3 Classifier Created.")


# Decision Tree
if load_classifiers[5]:
    try:
        decision_tree_classifier = pickle.load(open("decision_tree_classifier.p", "rb"))
        print("Decision Tree Classifier Loaded.")

    except EOFError:
        print("Decision Tree end of file error.")

    except FileNotFoundError:
        print("Decision tree not loaded, needs to be trained...")
        decision_tree_classifier = ExtraTreesClassifier(n_estimators=20)
        decision_tree_classifier.fit(X_dict_array_train, y_array_train)
        pickle.dump(decision_tree_classifier, open("decision_tree_classifier.p", "wb"))
        print("Decision tree classifier Created.")

dummy_classifier = DummyClassifier()
dummy_classifier.fit(X_dict_array_train, y_array_train)
predicted = dummy_classifier.predict(X_dict_array_test)
print(Colors.CYAN + "Dummy Classifier:" + Colors.RESET)
print(metrics.classification_report(y_array_test, predicted))
print("\n\n")


vote_array = [[0 for x in range(15)] for x in range(X_dict_array_test.shape[0])]
if load_classifiers[0]:
    try:
        print(Colors.CYAN + "tfidf Classifier" + Colors.RESET)
        score_individual_frames(X_array_test, tfidf_ovr_classifier)
    except NameError:
        print("tfidf Classifier is not loaded or created.")

if load_classifiers[1]:
    try:
        print(Colors.CYAN + "One Vs Rest Linear SVC Classifier" + Colors.RESET)
        score_individual_frames(X_dict_array_test, one_vs_rest_classifier)
        vote_on_frames(X_dict_array_test, vote_array, one_vs_rest_classifier, 25)
    except NameError:
        print("SVM Classifier is not loaded or created.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP sgd Neural Net Classifier" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_sgd_classifier)
        vote_on_frames(X_dict_array_test, vote_array, mlp_sgd_classifier, 25)
    except NameError:
        print("MLP SGD Classifier is not loaded or created.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP adam Neural Net Classifier" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_adam_classifier)
        vote_on_frames(X_dict_array_test, vote_array, mlp_adam_classifier, 25)
    except NameError:
        print("MLP adam Classifier is not loaded or created.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP lbfgs Neural Net Classifier" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_lbfgs_classifier)
        vote_on_frames(X_dict_array_test, vote_array, mlp_lbfgs_classifier, 25)
    except NameError:
        print("MLP lbfgs Classifier is not loaded or created.")

if load_classifiers[5]:
    try:
        print(Colors.CYAN + "Decision Tree Classifier" + Colors.RESET)
        score_individual_frames(X_dict_array_test, decision_tree_classifier)
        vote_on_frames(X_dict_array_test, vote_array, decision_tree_classifier, 25)
    except NameError:
        print("Decision Tree Classifier is not loaded or created.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP lbfgs 2" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_lbfgs_classifier2)
        vote_on_frames(X_dict_array_test, vote_array, mlp_lbfgs_classifier2, 25)
    except NameError:
        print("MLP lbfgs 2 Neural Net Classifier is not loaded or created.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP lbfgs 3" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_lbfgs_classifier3)
        vote_on_frames(X_dict_array_test, vote_array, mlp_lbfgs_classifier3, 25)
    except NameError:
        print("MLP lbfgs 3 Neural Net Classifier is not loaded or created.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP adam 2" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_adam_classifier2)
        vote_on_frames(X_dict_array_test, vote_array, mlp_adam_classifier2, 25)
    except NameError:
        print("MLP adam 2 classifier is not laoded or created.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP adam 3" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_adam_classifier3)
        vote_on_frames(X_dict_array_test, vote_array, mlp_adam_classifier3, 25)
    except NameError:
        print("MLP adam 3 classifier not created or loaded.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP adam 4" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_adam_classifier4)
        vote_on_frames(X_dict_array_test, vote_array, mlp_adam_classifier4, 25)
    except NameError:
        print("MLP adam 4 classifier not created or loaded.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP adam 5" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_adam_classifier5)
        vote_on_frames(X_dict_array_test, vote_array, mlp_adam_classifier5, 25)
    except NameError:
        print("MLP adam 5 classifier not created or loaded.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP sgd 2" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_sgd_classifier2)
        vote_on_frames(X_dict_array_test, vote_array, mlp_sgd_classifier2, 25)
    except NameError:
        print("MLP sgd 2 classifier not created or loaded.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP sgd 3" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_sgd_classifier3)
        vote_on_frames(X_dict_array_test, vote_array, mlp_sgd_classifier3, 25)
    except NameError:
        print("MLP sgd3 classifier not created or loaded.")

if load_classifiers[4]:
    try:
        print(Colors.CYAN + "MLP sgd 4" + Colors.RESET)
        score_individual_frames(X_dict_array_test, mlp_sgd_classifier4)
        vote_on_frames(X_dict_array_test, vote_array, mlp_sgd_classifier4, 25)
    except NameError:
        print("MLP sgd 4 classifier not created or loaded.")


vote_array_2 = [[0 for x in range(15)] for x in range(X_dict_array_test.shape[0])]

# Dummy classifier voting and testing
vote_on_frames(X_dict_array_test, vote_array_2, dummy_classifier, 25)
voting_classifier(vote_array_2, y_array_test, 25, False)


voting_classifier(vote_array, y_array_test, 100, False)
# x = 10
# score = 0
# x_val = 0
# while x <= 225:
#     print(Colors.GREEN + str(x) + Colors.RESET)
#     temp = voting_classifier(vote_array, y_array_test, x, False)
#     if temp > score:
#         score = temp
#         x_val = x
#     x += 5
#
# print("\n\n" + str(x_val) + "  :  " + str(score))



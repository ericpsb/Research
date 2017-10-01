# Imports
import json
import string
import nltk
import math
import random
from nltk import word_tokenize
import pickle
from nltk.corpus import stopwords
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class Colors:

    RED = "\033[1;31m"
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    BOLD = "\033[;1m"
    REVERSE = "\033[;7m"


# AnnotatedArticle class is used for the entire annotated article. It includes
# all of the annotation information including sentences, sources, date, title
# etc... Includes some processing of the original text
class AnnotatedArticle(object):

    def __init__(self, title, text, text_with_punctuation, source, date, annotations):

        self.sentences = []
        self.text = text
        self.text_with_punctuation = text_with_punctuation
        self.title = title
        self.source = source
        self.date = date
        self.annotations = annotations

        index = self.text.find("PRIMARY", 0, 30)
        self.text = self.text[index + 7:]
        index = self.text_with_punctuation.find("PRIMARY", 0, 30)
        self.text_with_punctuation = self.text_with_punctuation[index + 7:]
        self.sentences.append(Sentence("PRIMARY", -1))

        index = self.text.find(title)
        self.text = self.text[index + len(title):]
        tokenize_sentences = nltk.sent_tokenize(self.text_with_punctuation, language='english')

        count = 0
        for sentence in tokenize_sentences:
            self.sentences.append(Sentence(sentence, count))
            count += 1

    def to_string(self):
        annotation_print = ""
        for sentence in self.sentences:
            annotation_print += sentence.to_string() + "\n"
        return Colors.BLUE + "Title " + str(self.title) \
               + "\nSource: " + str(self.source) \
               + "\nSentences: \n" + Colors.RESET + annotation_print + "\n\n"


# Annotation class is used for individual annotations to be matched with sentences.
# Includes the original text, a text with punctuation removed, char locations for
# start and end points in reference to the original article text and a code / frame
# for the annotation.
class Annotation(object):

    def __init__(self, start, end, code, text, frame, text_with_punctuation, annotator):
        if text:
            while (len(text) > 0) and ((text[0] in "\n") or (text[0] in " ")):
                text = text[1:]
            text.replace("\n", " ")
            self.text = text
            self.text_with_punctuation = text_with_punctuation
            self.end = end
            self.start = start
            self.code = code
            self.frame = frame
            self.annotator = annotator

    def to_string(self):
        return "Start: " + str(self.start) + "\nEnd: " + str(self.end) \
               + "\nCode: " + str(self.code) \
               + "\nText: " + str(self.text) \
               + "\nFrame: " + str(self.frame) + "\n"


# Sentence class is used to store individual sentences with the original text, code and
# all applicable frames.
class Sentence(object):
    # Text of sentence
    text = ""
    text_pos = []
    text_ne = []
    label_list = ["PERSON", "ORGANIZATION", "GPE", "LOCATION"]
    feature_dict = {}

    # Features

    # How many words are in the sentence
    word_count = 0
    word_count_no_stops = 0
    # Compound, Simple, Complex, Compound-Complex
    sentence_type = ""

    # Position in document (offset from beginning)
    position = 0
    # Is there a named entity, empty is none. First is entity name second is location
    named_entity = {}
    is_ne_present = False


    def __init__(self, text, position):
        if text:
            while (len(text) > 0) and ((text[0] in "\n") or (text[0] in " ")):
                text = text[1:]
            self.text = text
            self.codes = []
            self.simple_codes = []
            self.two_gram = []
            self.one_gram = []
            self.three_gram = []
            self.frames = []
            self.annotator_tracker = []
            self.position = position
            self.word_count = len(text.split())

    def pos_process(self):
        self.text_pos = nltk.pos_tag(word_tokenize(self.text))

    def ne_process(self):
        self.text_ne = nltk.ne_chunk(self.text_pos)
        for x in self.text_ne.subtrees():
            if (x.label() != "S"):
                self.named_entity[x.label()] = x.leaves()
                self.is_ne_present = True
        self.feature_dict["Named Entity Bool"] = self.is_ne_present

    def sentiment_process(self):
        analyzer = SentimentIntensityAnalyzer()
        vs = analyzer.polarity_scores(self.text)
        return vs

    def create_n_grams(self, one_gram, two_gram, three_gram):
        last = ""
        last2 = ""
        words = word_tokenize(self.text)
        for word in words:
            if word not in stop:
                one_gram.append(word)
                if last != '':
                    two_gram.append([last, word])
                    if last2 != '':
                        three_gram.append([last2, last, word])
            last2 = last
            last = word
        self.word_count_no_stops = len(one_gram)

    def add_frame(self, code, frame, annotator):
        if (math.floor(code), annotator) not in self.annotator_tracker:
            self.annotator_tracker.append((math.floor(code), annotator))
            self.codes.append(code)
            self.simple_codes.append(math.floor(code))
            self.frames.append(frame)

    def to_string(self):
        return "Text: " + str(self.text) \
               + "\nFrames: " + str(self.frames) \
               + "\nPosition: " + str(self.position) \
               + "\nWord Count: " + str(self.word_count) + "\n"


# ---------------------------- Functions ----------------------------


# This function matches the annotations to the split sentences stored in the annotated
# articles objects.
def match_annotations_to_sentences(articles, verbose, error_verbose):

    error_print = 0
    annotation_count = 0
    total_repeats = 0

    for x0, article in enumerate(articles):
        for x1, annotation in enumerate(article.annotations):
            repeat_count = -1
            is_found = False
            start_buffer = 10
            start = annotation.start
            if verbose:
                print(Colors.CYAN + "\n\n\nAnnotated text seg: " + annotation.text + Colors.RESET)

            # First check for annotation match, simple comparison
            for x2, sentence in enumerate(article.sentences):
                if not is_found:
                    start = start - len(sentence.text)
                    start_buffer += 1
                    sentence_no_punctuation = ''.join(char for char in sentence.text
                                                      if char not in punctuation_list_no_period)
                    sentence_no_punctuation.replace("\n", " ")
                    if (annotation.text in sentence_no_punctuation) and (start <= start_buffer):
                        repeat_count += 1
                        sentence.add_frame(annotation.code, annotation.frame, annotation.annotator)
                        is_found = True
                        if verbose:
                            print("Sentences: " + sentence.text)
                            print(Colors.GREEN + "Added Frame: " + str(annotation.frame) + Colors.RESET)
                else:
                    break

            # Second annotation check, splits annotation into multiple sentences
            if not is_found:
                record = []
                split_annotation = nltk.sent_tokenize(annotation.text, language="english")
                for x3, sentence in enumerate(article.sentences):
                    for x4, split in enumerate(split_annotation):
                        sentence_no_punctuation = ''.join(ch for ch in sentence.text
                                                          if ch not in punctuation_list_no_period)
                        sentence_no_punctuation.replace("\n", " ")
                        if split in sentence_no_punctuation:
                            if len(split_annotation) <= 1:
                                repeat_count += 1
                                record.append(sentence.text)
                            is_found = True
                            sentence.add_frame(annotation.code, annotation.frame, annotation.annotator)
                            if verbose:
                                print("Sentence: " + sentence.text)
                                print(Colors.GREEN + "Added frame: " + str(annotation.frame) + Colors.RESET)

            # Third annotation check, splits annotation with punctuation still present
            if not is_found:
                split_annotation = nltk.sent_tokenize(annotation.text_with_punctuation, language='english')
                for x5, sentence in enumerate(article.sentences):
                    for x6, split in enumerate(split_annotation):
                        sentence_no_punctuation = ''.join(ch for ch in sentence.text
                                                          if ch not in punctuation_list_no_period)
                        sentence_no_punctuation.replace("\n", " ")
                        trimmed_split = ''.join(ch for ch in split if ch not in punctuation_list_no_period)
                        trimmed_split.replace("\n", " ")
                        if trimmed_split in sentence_no_punctuation:
                            if len(split_annotation) <= 1:
                                repeat_count += 1
                                record.append(sentence.text)
                            is_found = True
                            sentence.add_frame(annotation.code, annotation.frame, annotation.annotator)
                            if verbose:
                                print("Sentence: " + sentence.text)
                                print(Colors.GREEN + "Added frame: " + str(annotation.frame) + Colors.RESET)

            # Error printing, records when an annotation is not found, or repeats
            if not is_found:
                error_print += 1
                if error_verbose:
                    print(Colors.RED + "Error finding match for annotation." + Colors.RESET)
                    print("Annotation text: " + annotation.text)
                    print("Article title: " + article.title)
                    print("Article text: ")
                    for x7 in article.sentences:
                        sentence_no_punctuation = ''.join(ch for ch in x7.text if ch not in punctuation_list_no_period)
                        sentence_no_punctuation.replace("\n", " ")
                        print(sentence_no_punctuation)
                    if annotation.text in article.text:
                        print(Colors.GREEN + "FOUND" + Colors.RESET)
                        print("\n\n\n")
            else:
                annotation_count += 1

            if repeat_count >= 1:
                if error_verbose:
                    print(Colors.RED + "Repeated annotation: " + Colors.BLUE + str(repeat_count) + Colors.RESET)
                    print("Annotation text: " + annotation.text)
                    print("Frame: " + annotation.frame)
                    print(record)
                    print("\n\n")  # '''
                total_repeats += repeat_count

    return [error_print, annotation_count, total_repeats]


# Create articles goes through the correct json and creates article objects for each article
# present in the json.
def create_articles(articles, information_json):
    total_articles = 0
    empty_count = 0

    count = 0
    for x8, key in enumerate(information_json.keys()):
        temp_title = information_json.get(key).get('title')
        temp_title = ''.join(char for char in temp_title if char not in punctuation_list_no_period)
        temp_text = information_json.get(key).get('text')
        temp_source = information_json.get(key).get('source')
        temp_day = information_json.get(key).get('day')
        temp_month = information_json.get(key).get('month')
        temp_year = information_json.get(key).get('year')
        temp_date = temp_day + "-" + temp_month + "-" + temp_year
        annotation_list = []

        found = False
        for x in held_out:
            if temp_title == x.title and temp_date == x.date:
                found = True

        if not found:
            is_empty = True
            for x9, index in enumerate(information_json.get(key).get('annotations').get('framing').keys()):
                all_list = information_json.get(key).get('annotations').get('framing')[index]

                temp_annotator = index
                for annotation in all_list:
                    is_empty = False
                    temp_start = annotation.get('start')
                    temp_end = annotation.get('end')
                    temp_code = annotation.get('code')
                    temp_type = code_dictionary[str(temp_code)]
                    if len(temp_text) > temp_start:
                        character_1 = (temp_text[temp_start])
                        character_2 = (temp_text[temp_start - 1])
                        if any(char in punctuation_list for char in character_1):
                            temp_quote = temp_text[temp_start + 1:temp_end]
                        elif any(char in punctuation_list for char in character_2):
                            temp_quote = temp_text[temp_start:temp_end]
                        else:
                            temp_quote = temp_text[temp_start - 1:temp_end]
                        temp_quote_no_punctuation = ''.join(char for char in temp_quote
                                                            if char not in punctuation_list_no_period)
                        temp_quote_no_punctuation.replace("\n", " ")
                        temp_annotation = Annotation(temp_start, temp_end, temp_code,
                                                     temp_quote_no_punctuation, temp_type, temp_quote, temp_annotator)
                        annotation_list.append(temp_annotation)

            temp_text_no_punctuation = ''.join(char for char in temp_text
                                               if char not in punctuation_list_no_period)
            temp_article = AnnotatedArticle(temp_title, temp_text_no_punctuation,
                                            temp_text, temp_source, temp_date, annotation_list)
            total_articles += 1
            if (is_empty):
                empty_count += 1
            else:
                articles.append(temp_article)
            count += 1
    print("Empty Frames: " + str(empty_count) + " / " + str(total_articles)
          + "   " + str(empty_count/total_articles*100) + "%")
    return


# ---------------------------- Main ----------------------------


# Create punctuation lists
punctuation_list = set(string.punctuation)
punctuation_list_no_period = set(string.punctuation.replace(".", ""))
punctuation_list_no_period.remove("-")
punctuation_list_no_period.remove("?")
stop = set(stopwords.words('english'))
stop.update(['.', ',', '$', "''", '``', '"',
             "'", '?', '!', ':', ';', '(', ')',
             '[', ']', '{', '}', '--', 'n\'t', '-',
             'primary', '\'s'])
# articles = []

with open('codes.json') as code_file:
    codes = json.load(code_file, encoding="utf-8")
code_dictionary = {}
for x, key in enumerate(codes.keys()):
    code_dictionary[str(key)] = str(codes.get(key))

# Open the relevant files, the codes.json as well as immigration, smoking, and samesex .json files
def main(load):
    if (load):
        files = []
        with open('smoking.json') as information_file:
            information_json = json.load(information_file, encoding='utf-8')
        files.append(information_json)

        with open('immigration.json') as information_file:
            information_json = json.load(information_file, encoding='utf-8')
        files.append(information_json)

        with open('samesex.json') as information_file:
            information_json = json.load(information_file, encoding='utf-8')
        files.append(information_json)

        annotated_articles = []
        names = ["smoking", "immigration", "samesex"]
        count = 0
        # Create the articles and match annotations to sentences
        for information in files:
            articles = []
            create_articles(articles, information)
            error = match_annotations_to_sentences(articles, False, False)

            # Print out total error rates
            print("\nArticles: " + str(len(articles)))
            print("Completed Annotation matching.")
            print("Total errors: " + str(error[0]))
            print("Correct annotations: " + str(error[1]))
            print("Error rate: " + str(round(error[0] / error[1] * 100, 4)) + "%")
            print("Repeats: " + str(error[2]))
            print("Repeat rate: " + str(round(error[2] / error[1] * 100, 4)) + "%\n\n")
            annotated_articles.append((names[count], articles))
            count += 1
        pickle.dump(annotated_articles, open("annotations_human_metrics.p", "wb"))

full_test = False
if (full_test):
    annotated = pickle.load(open("annotations.p", "rb"))
    held_out = []
    for x in range(3):
        for a in annotated[x][2]:
            held_out.append(a)

main(full_test)
annotations_metrics = pickle.load(open("annotations_human_metrics.p", "rb"))
count0 = 0
count1 = 0
count2 = 0
for x in range(3):
    for annot in annotations_metrics[x][1]:
        for x in annot.sentences:
            test_array = [0 for m in range(15)]

            for y in x.annotator_tracker:
                test_array[y[0] - 1] += 1

            for y in test_array:
                if y == 0:
                    count0 += 1
                if y == 1:
                    count1 += 1
                if y >= 2:
                    count2 += 1

print (count0)
print (count1)
print (count2)
print("\n")

union = 2 * (count2 + count1)
print(union)
recall = (union - count1) / (union)
print(recall)
f_score = (2 * recall) / (1 + recall)
print(f_score)
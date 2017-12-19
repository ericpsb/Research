from app import app
from flask import request
from flask import jsonify
# from nltk.tokenize import sent_tokenize, word_tokenize
import SentenceData
import Clean_Process_Frames
import json
import math
from nltk.tokenize import sent_tokenize, word_tokenize

# g_json['url'] = given url
# g_json['content'] = content from article

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/json', methods=['GET', 'POST'])
def receive_json():
	#var = "Input URL: " + str(g_json['url'])
	myJson = request.get_json()
	if myJson is None:
		print "ERROR: myJson is none!"
		return "ERROR: no content received!"
	else:
		print "Content received from " + myJson['url']
		output = new_sentence_data(myJson['content'])
		# output = [sentences, index_dictionary, vote_array]
		
		# Separate out the parts of the output:
		sentences = output[0]
		index_dictionary = output[1]
		vote_array = output[2]
		display = output[3]

		# print str(sentences[1])
		# print str(index_dictionary[2])
		# print str(vote_array[1][2])
		# vote_array[sentence_no][frame_no]

		outputJsonObj = {}
		for i in range(len(sentences)):
			outputJsonObj[str(i)] = { "content": sentences[i] }
			for j in range(len(index_dictionary)):
				outputJsonObj[str(i)]["f" + str(j)] = vote_array[i][j]
		print "Example entry for Sentence 1: " + str(outputJsonObj[str(0)])

		return jsonify(outputJsonObj)		# this is the GET value returned back to the server

def new_sentence_data(text):
	stop = SentenceData.stop
	sentences = sent_tokenize(text, language='english')
	sentence_count = 0
	dict_array = []

	for index in range(len(sentences)):
	    one = []
	    two = []
	    three = []
	    temp = Clean_Process_Frames.Sentence(sentences[index], index)
	    temp.pos_process()
	    temp.ne_process()
	    vs = temp.sentiment_process()
	    temp.create_n_grams(one, two, three)
	    sentence_count += 1
	    temp_feature_dict = {}

	    words = [i for i in word_tokenize(temp.text) if i.lower() not in stop]
	    temp_feature_dict["sentiment_score"] = math.fabs(vs.get('compound'))
	    if temp.position < 2:
	        temp_feature_dict["is_first"] = 1
	    else:
	        temp_feature_dict["is_first"] = 0

	    vivid_score = 0
	    average_concrete = 0
	    highest_concrete = 0
	    highest_abstract = 0

	    for x in words:
	        if x.lower() in SentenceData.vivid_dict:
	            vivid_score += float(SentenceData.vivid_dict.get(x.lower()))
	        if x.lower() in SentenceData.concrete_dict:
	            average_concrete += float(SentenceData.concrete_dict.get(x.lower()))
	            if float(SentenceData.concrete_dict.get(x.lower())) > highest_concrete:
	                highest_concrete = float(SentenceData.concrete_dict.get(x.lower()))
	            if float(SentenceData.concrete_dict.get(x.lower())) < highest_abstract:
	                highest_abstract = float(SentenceData.concrete_dict.get(x.lower()))
	        temp_string = "1gram_"
	        temp_string += SentenceData.convert_words_to_features(x, SentenceData.word_dictionary,
	                                                              SentenceData.word_index)
	    temp_feature_dict["highest_concrete"] = highest_concrete
	    temp_feature_dict["highest_abstract"] = highest_abstract
	    if len(words) > 0:
	        vivid_score = vivid_score / len(words)
	        average_concrete = average_concrete / len(words)
	    else:
	        vivid_score = 0

	    temp_feature_dict["vivid_score"] = vivid_score
	    temp_feature_dict["average_concrete_score"] = average_concrete
	    for x in two:
	        temp_string = "2gram_"
	        temp_string += SentenceData.convert_grams_to_features(x, SentenceData.bi_gram_dictionary,
	                                                              SentenceData.bi_gram_index)
	        temp_feature_dict[temp_string] = 1

	    for x in three:
	        temp_string = "3gram_"
	        temp_string += SentenceData.convert_grams_to_features(x, SentenceData.tri_gram_dictionary,
	                                                              SentenceData.tri_gram_index)
	        temp_feature_dict[temp_string] = 1

	    if temp.is_ne_present:
	        temp_feature_dict["is_ne_present"] = 1
	    else:
	        temp_feature_dict["is_ne_present"] = 0

	    dict_array.append(temp_feature_dict)

	X_dict_array = SentenceData.vectorizer.transform(dict_array)

	vote_array = [[0 for x in range(45)] for x in range(len(sentences))]
	SentenceData.vote_on_frames(X_dict_array, vote_array, SentenceData.one_vs_rest_classifier, 25)
	SentenceData.vote_on_frames(X_dict_array, vote_array, SentenceData.mlp_sgd_classifier, 25)
	SentenceData.vote_on_frames(X_dict_array, vote_array, SentenceData.mlp_adam_classifier, 25)
	# SentenceData.vote_on_frames(X_dict_array, vote_array, SentenceData.mlp_lbfgs_classifier, 25)
	# SentenceData.vote_on_frames(X_dict_array, vote_array, SentenceData.mlp_lbfgs_classifier2, 25)
	# SentenceData.vote_on_frames(X_dict_array, vote_array, SentenceData.mlp_lbfgs_classifier3, 25)


	SentenceData.vote_on_frames(X_dict_array, vote_array, SentenceData.mlp_adam_classifier2, 25)
	SentenceData.vote_on_frames(X_dict_array, vote_array, SentenceData.mlp_adam_classifier3, 25)
	#SentenceData.vote_on_frames(X_dict_array, vote_array, SentenceData.mlp_adam_classifier5, 25)
	return SentenceData.voting_classifier_new(vote_array, sentences, 25, True)


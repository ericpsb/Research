import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model, decomposition, datasets
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import train_test_split
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import confusion_matrix
from sklearn.metrics import average_precision_score
from sklearn.metrics import classification_report
from sklearn.dummy import DummyClassifier
import numpy 

def main():
	df = pd.read_csv("ego_alter.csv")
	data = numpy.array(df)

	X = data[:,0:49]
	Y = data[:,54]
	x_train, x_test, y_train, y_test = train_test_split(X,Y,test_size = 0.3)
	print len(y_test)

	logistic = linear_model.LogisticRegressionCV(cv = 10)
	# logistic = linear_model.LogisticRegression()

	# print "summary", logistic.summary()
	logistic.fit(x_train, y_train)
	print "coefficient: ", logistic.coef_
	# print "get_params", logistic.get_params(deep = True)

	prediction = logistic.predict(x_test[:])
	print len(prediction)
	error = prediction - y_test
	print "error: ", error
	error_rate = sum(numpy.square(error))/(500.0*0.3)
	print "Accuracy: ", 1-error_rate #0.84
	print y_test
	print prediction
	print confusion_m(prediction,y_test)
	# print confusion_matrix(y_test,prediction)
	dummy = DummyClassifier(strategy='stratified', random_state=None, constant=None)
	dummy.fit(x_train,y_train)
	dummy_pred = dummy.predict(x_test)
	error = dummy_pred - y_test
	print "dummy error: ", error
	error_rate = sum(numpy.square(error))/(500.0*0.3)
	print "dummy Accuracy: ", 1-error_rate #0.84
	print y_test
	print dummy_pred
	print "dummy confusion matrix ", confusion_m(dummy_pred,y_test)

	

	# target_names = ['class 0','class 1']
	# print classification_report(y_test, prediction, target_names=target_names)

	# print "score: ", logistic.fit(x_train,y_train).score(x_test,y_test)
	precision, recall, thresholds = precision_recall_curve(y_test,logistic.decision_function(x_test),pos_label = 1)
	# average_precision = average_precision_score(y_test,logistic.decision_function(x_test))
	f_score = 2 * precision * recall / (precision + recall)
	print "f-score: ", f_score

	plt.clf()
	plt.plot(recall[0], precision[0], label='Precision-Recall curve')
	for i in range(len(precision)):
		# print recall[i],precision[i]
		plt.scatter(recall[i], precision[i])
	plt.xlabel('Recall')
	plt.ylabel('Precision')
	plt.ylim([0.0, 1.05])
	plt.xlim([0.0, 1.0])
	# plt.title('Precision-Recall example: AUC={0:0.2f}'.format(average_precision[0]))
	plt.legend(loc="lower left")
         
	plt.show()


	# print "transform: ", logistic.transform(x_train)[0] #20

	# summary
	# df.describe()
	# df.hist()
	# plt.show()

	# pca = decomposition.PCA()
	# logistic = linear_model.LogisticRegression()
	# pipe = Pipeline(steps=[('pca', pca), ('logistic', logistic)])
	# pca.fit(X)
	
	# n_components = [15, 30, 49]
	# Cs = numpy.logspace(-4, 4, 3)

	# estimator = GridSearchCV(pipe,
	#                      dict(pca__n_components=n_components,
	#                           logistic__C=Cs))
	# estimator.fit(X, Y)

	# plt.axvline(estimator.best_estimator_.named_steps['pca'].n_components,
	#             linestyle=':', label='n_components chosen')
	# plt.legend(prop=dict(size=12))
	# plt.show()

def confusion_m(prediction,true):
	result = [[0,0],[0,0]]
	for i in range(len(true)):
		if (true[i] == 0):
			if (prediction[i] == 0):
				result[0][0] = result[0][0] + 1
			elif (prediction[i] == 1):
				result[0][1] = result[0][1] + 1
		elif (true[i] == 1):
			if (prediction[i] == 0):
				result[1][0] = result[1][0] + 1
			elif (prediction[i] == 1):
				result[1][1] = result[1][1] + 1
	return result

if __name__ == "__main__":
	main()
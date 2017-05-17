# topicmodeling

First, mallet.zip is a compressed file that contains data from early runs of mallet. The different runs contain different stop word lists and number of topics used. 

The mallet2 folder contains the later runs of topic modeling, particularly when the stop word list was finalized. In it, we have quite a few files and directories.
	
	- autismtopics.R uses blog.stop (stop word list) and merged_file.json (blog data) to create topic modeling analysis. In the R script, we create a data frame called docs.and.topics that has each post with the 50 topic proportions.

	- auxillary.R contains code to create corrgrams and other plots using the docs.and.topics output

	- DataAnalysis contains data statistics on the corpus as well as several plots to show spread of things like words per post and posts per blog.

	- finalRun contains the R data file from the final run. To view the data, just load run5data.RData into RStudio and you will be able to see output from that run in the docs.and.topics data frame. Additionally it contains an annotated outfile with the topics reoresented in the top 20 words as well as a description of the topic and snippets from representative posts. 

	-otherRuns contains similar folders to finalRun with slight modifications. For example, there is a run with 100 topics generated. 

	-dendrogramStuff contains code written to merge topics based on similarities. The code did not produce a proper dendrogram so there is still issues with it. 
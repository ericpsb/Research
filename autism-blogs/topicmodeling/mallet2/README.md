README for folder "mallet2"

This folder contains the more-recent runs of topic modeling,
performed once the stop word list was finalized in addition to
files needed to perform the topic modeling.

NOTE: A copy of "merged_file.json" must be moved into this folder
before topic modeling can be performed.

"blog.stop" - the current list of stop words

"autismtopics.R" - an R Script that uses the stop word list and
the blog data to create topic modeling analysis; the output is
a data frame called "docs.and.topics" that has each post with
its 50 topic proportions

"auxillary.R" - an R Script capable of creating corrgrams and
other plots using the "docs.and.topics" data frame

"visualizationBuilder.R" - an R Script that uses the "docs.and.topics"
data frame to normalize dates, average topic proportions, and 
generate the three CSV files in this folder in addition to
"totalposts.js" and "yearlydata.js," found in the "visualization" folder
and used for the Cosine Visualization

"cosineFormatData.py" - a Python script that converts
"agTotal.csv" into a JavaScript file, "cosineData.js," which is
usable for the Cosine Visualization; "cosineData.js" is housed
in the "visualization" folder with the other JavaScript files

"ag.csv" - a CSV file containing the topic proportions for the
blogs on a weekly basis

"agYearly.csv" - a CSV file containing the topic proportions
for the blogs in addition to the number of posts on a yearly basis

"agTotal.csv" - a CSV file containing the topic proportions for
the blogs overall

"DataAnalysis" - a folder containing data statistics on the
corpus as well as several plots to show the distribution of
things such as words per post and posts per blog

"finalRun" - a folder containing the R data file from a recent
run, viewable by loading run5data.RData into RStudio; also
contains an annotated outfile with the topics reoresented by
their top 20 words as well as a description of the topic
and snippets from representative posts

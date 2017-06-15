# nodeLDA

This folder contains sources to code that generates a webpage that displays the topics, correlations, topic correlations, and time series from the results of topic modeling

This code require data generated from other part of the autism blog project in order to function.
Some software needed: python, bash (or any linux shell), R + RStudio
<ol>
<li>Perform blog scraping in the blogscraper/specificBlogs directory, the scrape.sh file should automates the web scraping(not tested), if the script failes, run the scraper.py manually in each subdirectory, this step might takes a few hours, also if the python script throws error, update your python version.</li>
<li>Run the merge.py to merge the data from each folder, this should generate a file called merged_file.json</li>
<li>Move to topicmodeling\mallet2 directory, moved the merged_file.json to there, and run autismtopics.R, you'll need to change the setwd() to point to your local directory, if rJava or .jinit gives error, consider remove JAVA_HOME envirenment variable and check if your java directory is in your PATH environemnt variable</li>
<li>Save the doc.topics.frame variable after the R script is finished with write.csv(doc.topics.frame, file="topic_frame.csv", quote=FALSE), this will produce topic_frame.csv</li>
<li>run the processblog.py, this will produce the documents.txt file</li>
<li>then have documents.txt and topic_frame.csv in this folder</li>
<li>use node to run nodeLDA.js, this will generate a file called nodeLDA.json file</li>
<li>use node to run server.js to launch the server itself</li>
</ol>

the webpage and some javascript are modified version of the jsLDA project: https://github.com/mimno/jsLDA
The original version (jsLDA) loads the scraped blogs and performs topic modeling on the fly, which causes the client to perform all the processing (require good processor), also due to the limit on browser memory, there is a limit to the amount of blog data. So this solution is not optimal nor does it work on our huge set of data.
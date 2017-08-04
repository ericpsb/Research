# nodeLDA

This folder contains sources to code that generates a webpage that displays the topics, correlations, topic correlations, and time series from the results of topic modeling. 

Softwares required: python, bash (or any linux shell), R + RStudio, java, and node

The code requires the output from web scraping to start, if haven't done so, do the following:
<ol>
<li> Perform blog scraping in the blogscraper/specificBlogs directory, the scrape.sh file should automates the web scraping(not tested), if the script failes, run the scraper.py manually in each subdirectory, this step might takes a few hours, also if the python script throws error, update your python version. </li>
<li> Run the merge.py to merge the data from each folder, this should generate a file called merged_file.json, and move the file to the current directory. </li>
</ol>

Procedure for performing nodeLDA: (Step 1-3 are recommended to run on your local machine)
<ol>
<li>run autismtopics.R using RStudio, you'll need to change the setwd() to point to your local directory (this folder), if rJava or .jinit gives error, consider remove JAVA_HOME envirenment variable and check if your java directory is in your PATH environemnt variable. The script will produce topic_frame.csv and filtered_merged_file.json</li>
<li>run processblog.py using python, this will produce the documents.txt</li>
<li>run nodeLDA.js using node, this will generate a file called nodeLDA.json</li>
<li>move the following files to the server: server.js, nodeLDA.json, jsLDA.css, and jsLDA.js</li>
<li>run server.js to start the server, this can also be done on the local machine for testing purpose</li>
</ol>

the webpage design and computations are based on the jsLDA project: https://github.com/mimno/jsLDA <br>
The original version (jsLDA) loads the scraped blogs and performs topic modeling on the fly, having the client (browser) done all the computations. Due to limitations on browser history, this is not ideal or impossible for larger sets of document data. <br>
NodeLDA performs a set of preprocessing of the data on the server side and simply serve the results to the client upon requests, this removes the limit on the amount of documents and contents, but inevitably removes the ability to perform different LDA runs and see different results on demand.
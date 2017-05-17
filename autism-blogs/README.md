# autism-blogs

This repository contains code to scrape blogs and analyze them using topic modeling.
The code is split up into three parts.

The first part is the folder labeled blogscrapers. This folder contains three python scripts
used to scrape blogs of all archived posts. The three scripts are used to scrape sites made on
wordpress, typepad and blogspot. Additionally, the specificblogs folder contains all of the scrapers used for each of the specific blogs.

The second part of the folder is called topicModeling. It contains all of the code and data generated from topic modeling in R. the mallet zip file contains all of the initaial runs that I used to play around and get familiar with using the stop word list. The mallet2 folder contains the latest runs with the finalized stop word list. The last run used for the visualizations and discussed in our meetings is located in the folder finalRun.

The final part of the folder is called visualization. This contains R code to normalize dates and export data in the appropriate format for the sliding heatmap visualization. It also contains a bunch of d3 and slider files used in the visualizations. cosineVisualization is the one that displays the blogs in a circle and allows you to see how similar certain blogs are on certain topics.heatmapVisualization is the one the allows the user to use sliders to view temporal changes in topic proportions. 
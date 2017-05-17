# visualization

This folder contains the necessary components for creating two visualizations:
	
	1. cosineVisualization - inspired by the Stanford project http://nlp.stanford.edu/projects/dissertations/browser.html, this visualization allows you to see similarities across blogs over a selection of topics. The visualization uses the d3 and JQuery libraries included in the visualization folder.

	2. heatmapVisualization - this visualization uses the d3, JQuery, and JQRangeSlider libraries. The visualization allows you to view a heatmap at any given week from the first blog post to the last blog post. Notes: On the date range slider, we have a range of dates, but we use the date on the left(earlier one). The dict.txt is saved as a javascript variable in data.js and used in the heatmapVisualization file.


We also have the following:
	
	- visualizationBuilder.R is used to normalize the dates and average topic proportions over weeks and finally, output ag.csv. The data folder uses ag.csv and a formatdata.py script to create a dictionary data structure for the heatmapVisualization.
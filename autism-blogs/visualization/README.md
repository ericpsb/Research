README for folder "visualization"

This folder contains the necessary components for creating two
visualizations:
	
cosineVisualization - inspired by the Stanford project
http://nlp.stanford.edu/projects/dissertations/browser.html,
this visualization allows you to see similarities across blogs
over a selection of topics; uses d3 and JQuery libraries

heatmapVisualization - this visualization allows you to view a
heatmap at any given week from the first blog post to the last
blog post; uses d3, JQuery, and JQRangeSlider libraries
	Notes: On the date range slider, we have a range of
	dates, but we use the date on the left (earlier one). The
	"dict.txt" is saved as a javascript variable in "data.js" and
	used in the heatmapVisualization file

"cosineData.js" - a JavaScript file containing data from "ag.csv" (ie.
topic proportions for each blog)

"totalposts.js" - a JavaScript file containing the total number of
posts Scraped from each blog

"yearlydata.js" - a JavaScript file containing data from
"agYearly.csv" (ie. topic proportions and number of posts by year)

"cosineVisualization.html" - the HTML file that creates the Cosine
Visualization using the above JavaScript files and extensive
embedded JavaScript code
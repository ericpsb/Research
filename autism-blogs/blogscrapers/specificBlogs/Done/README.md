README for folder "Done"

This folder contains blog folders for each blog whose Scraper
is currently working.

Each folder contains:
	"scraper.py" - the Scraper script for the blog
	"scraper.pyc" - the executable version of the Scraper
	script
	"data.json" - the most recent JSON file for the blog
	"links.json" and "linksb.json" - outdated JSON files for
	the blog
One or more folders contain:
	"geckodriver.log" - output generated by the Scraper script
	"bug.txt" - extra JSON objects
	"dates.json" - an additional JSON object to compensate for
	"links.json" and "linksb.json" lacking dates
	"errors.txt" - a file describing any ongoing issues
	"dup.py" and "dup.pyc" - supplementary Python
	script/executable
	
To run the Scrapers:
	Install scrapy and selenium (pip install scrapy, pip install selenium)
	Go to the command line and navigate to the correct directory
	Run the command "scrapy runspider scraper.py -o data.json"
This will Scrape the blog into a file called "data.json"
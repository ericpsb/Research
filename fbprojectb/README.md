TrueFriend  
Lehigh University DAS Lab and Cornell Interaction Design Lab  
Led by Professor Eric Baumer  
https://das-lab.org/truefriend  
https://github.com/ericpsb/Research/tree/master/fbprojectb

Last updated: September 10, 2017 by Peter Schaedler (pwschaedler)

# Overview
TrueFriend is a website/Facebook app that infers the degrees of friendship between people based on the frequency of online interactions, and thus finds the "true friends" of a user. By using the Facebook Graph API, TrueFriend requests every item in a user's feed and stores it in a MongoDB database. From there, Python scripts process the information into two representations: 1) individual interactions, such as comments, which include the users involved and the posts from which they were gathered, and 2) JSON to represent the nodes and links that will be loaded into a D3.js force-directed graph. Each node represents a person on Facebook, and two nodes are connected if there is some interaction between them on the user's timeline. The more they interact, the closer the nodes will be.

# Software Architecture
The program consists mainly of three parts: front-end HTML, JavaScript, and PHP; back-end PHP scripts; and back-end Python scripts.

## Program Flow
When the user nagivates to https://das-lab.org/truefriend, they will arrive at `index.php`, where they can log into Facebook. From there, they will be redirected to `callback.php`, which has PHP code to run `ltget.py` on the server. From here, the user can click "Proceed to Visualization" and go to `initViz.php` which gives some basic statistics about the user's Facebook account. When the visualization has been generated, they will then be able to go to `viz.php`, which shows the full force-directed graph. In the background, `ltget.py` calls `update_db_v4.py`, which in turn makes use of `viz_generator.py`.

## Descriptions of Individual Files
### Front-End
`bootstrap.css`
> Twitter Bootstrap CSS styles. I haven't checked if this file is being used or not. It could just be grabbed from a CDN, though having it local is slightly faster.

`callback.php`
> The page a user is redirected to once they log in. The PHP code starts running the `ltget.py` script on the server, and the page displayed just includes a link that either goes to `initViz.php` or `viz.php`, depending if the user's visualization is ready or not.

`index.php`
> The main login page.

`initViz.php`
> A page with some basic statistics for the user that can be gleaned from scraping their Facebook profile. It displays this information and some graphs regarding relative friend counts compared to users in the database and the world to hold the user over until their visualization is ready.

`style.css`
> Some basic CSS styles.

`viz-d3.js`
> The JavaScript used in `viz.php` pertaining to the D3.js force-directed graph visualization.

`viz-doc.js`
> The JavaScript used in `viz.php` pertaining to the Top 5 Friends feature, and the page manipulation that goes along with that.

`viz-fb-load.js`
> The JavaScript used in `viz.php` pertaining to acquiring Facebook access credentials.

`viz-styles.css`
> A stylesheet just for `viz.php`.

`viz.php`
> The page where the user seems the main visualization. It's a D3.js force-directed graph that shows the user their "true friend interactions". Also on the page is the Top 5 Friends feature, which shows the user's top 5 friends based on the graph algorithm (a.k.a. which users have the strongest link strength with the user). The user can view their top 5 friends and post the result to Facebook.

`Woo10/`
> A folder containing some sample code and styles that much of the site is based on.

### Back-End PHP
`backendData.php`
> PHP script to access the Mongo database and retrieve visualization data.

`backendInit.php`
> PHP script to check if user is in database at start of program.

`IDsFromTaggableFriends.php`
> Gets IDs of users from Top 5 Friends list for taggable friends tagging in Facebook post.

`topFiveFriends.php`
> Determines top 5 friends according to the visualization algorithm and returns their names and IDs.

### Back-End Python
`config.py`
> Python file to provide easier Python access to what's in `config.ini`. Also provides a function to create the connection string for the database, since it requires grabbing a password from an environment variable.

`emptyDatabase.py`
> Empties both databases used by the program to attain a fresh start. Does __not__ conform to what databases/collections are specified in `config.ini`.

`ltget.py`
> Script that gets started by callback.php to begin back-end processing. Collects basic Facebook profile information about the user and puts into the database, then passes off to `update_db_v4.py` for the rest of the processing.

`mongo_access.py`
> Provides a few functions through the `MongoAccess` class for convenient access to Mongo DB from Python with a single open connection.

`new_viz_db_delete.py`
> Test file that deletes the information in the database that would be creatd by `newViz.py`. Does __not__ conform to what databases/collections are specified in `config.ini`.

`newViz.py`
> An old file that took the huge documents created by `query.py` and turned them into interactions by pairs of people, and also generated the JSON for the visualizations. No longer used in the program, but some things in the new version (see `viz_generator.py`) don't work exactly as they used to, so this may be worth looking at.

`newVizTest.py`
> A small test file I used for `newViz.py`. No longer necessary since `newViz.py` is no longer used in the program.

`query.py`
> An old file that took raw feed items and transformed them into monstrous documents that didn't make much sense. No longer used in the program, but some things in the new version (see `viz_generator.py`) don't work exactly as they used to, so this may be worth looking at.

`update_db_v4.py`
> Scrapes user data from Facebook and processes into two things: JSON to be used in the visualization, and individual "interactions" that show one discrete thing that two people have in common.

`viz_generator.py`
> Called by `update_db_v4.py`, this script takes care of the main processing into JSON and individual interactions.

### Other Files
`classification/` (only in repo)
> Old folder with stuff that isn't currently relevant to the project. Probably has something to do with machine learning?

`config.ini`
> Configuration file for database paths and hopefully other things later.

`formats.txt` (only in repo)
> Just some notes on the formats of different "objects" and what I've been calling "interaction arrays" (effectively individual interactions between people stored as arrays with a specific meaning at each index) and what they mean.

`mongo_install.bash`
> An install script for MongoDB. I didn't use it when we moved to Saiph, but everything worked out okay.

### Old Files
There is a folder called `unused_old_files`. Technically, these files should just be deleted, since they don't affect the program whatsoever. But for convenience and because I'm a code hoarder, I've placed these files in a folder to keep them out of the way.

## Database Information
The MongoDB database is currently stored on Eltanin, with the following databases and collections:
- fb_nonuse (Where raw Facebook data scraped from users is stored)
    - events (Scraped events from Facebook)
    - feeds (Scraped news feed items from Facebook)
    - friends (Scraped lists of people who are friends with users from Facebook)
    - interactions (Where half-baked processed interactions used to live, before the Great Refactor of 2017; shouldn't be necessary anymore)
    - likes (Scraped page likes from Facebook)
    - mutual (Scraped mutual friends from Facebook)
    - people (Scraped people in general from Facebook)
    - taggable_friends (Scraped taggable_friends lists from Facebook)
    - user (Scraped user information from Facebook)
- fb_nonuse_test (A testing database)
    - *same as fb_nonuse*
- fb_nonuse_test2 (A testing database, but also the most currently used, and with the most up-to-date information of test users)
    - *same as fb_nonuse*
- fbapp-DB (Where information about users and processed interactions are stored)
    - fb-interactions (Processed interactions between pairs of people)
    - fb-users (Individual users of the app and their information, including the JSON for their visualization)
- fbapp-DB_test (A testing database)
    - *same as fbapp-DB*
- fbapp-DB_test2 (A testing database, but also the most currently used, and with the most up-to-date information of test users)
    - *same as fbapp-DB*
- newVizTest (Database used for testing old feature; not necessary anymore)
    - app_interactions
    - nonuse_interactions
    - users
- test-database (Mongo test database)

# Requirements and Necessary Python Modules
General program requirements:
- Python 2.7
- PHP 7
- PHP MongoDB Driver (installed via Composer)
- jQuery
- D3.js
- Twitter Bootstrap

Necessary Python modules (can `pip install` these names as-is):
- pymongo
- simplejson
- python-dateutil
- apscheduler==2.1.2

Required background processes on Saiph:
- `autossh -M 20000 -L 27000:localhost:27017 -fN pws217@eltanin.cse.lehigh.edu` (should be run on login from `/etc/rc.local`, but if that doesn't work, run from `truefriend` user)

Required background processes on Eltanin:
- MongoDB 3.4 (run via `/usr/bin/mongod --config /etc/mongod.conf`)

# Accounts and Related Information
See Peter's user account on Saiph for this information.

# Known Issues
- MAIN ISSUE: Trying to get app approved by Facebook for taggable_friends use. Next thing to try is to make nodes on graph all be open by default (see node fill options in `viz-d3.js`) and only get filled in when confirmed that they are friends (via friends list). Continue with Top 5 Friends feature, but maybe try to get it to post as a "story"?
- `viz_generator.py` currently doesn't do anything with your given `friends` list (the friends of yours who have authorized the app) and `mutual` or `likes`. These were left out during the transition from `newViz.py` and `query.py`. Information from `mutual` and `likes` could be used to create other interactions for books/music in common, though from testing of `newViz` and `query`, I'm not sure they were ever being taken into account. The `friends` list may be necessary for the main issue above.
- "Go to Visualization" button in `initViz.php` will remain gray even after visualization is done unless you refresh. Maybe make it so it automatically changes?
- Emails about visualizations sometimes go to spam. No idea why.
- Every time you visit the site, it does the entire process all over. Maybe try to make it only process changes since last time.
- Posts on FB that are only links with no other text will show up as just black boxes on the viz pop-up.
- In pop-ups, pronouns are always masculine (he/him). Use Facebook's correct given gender or make them neutral.
- Logging throughout should be added.
- `vizDone` property in database for users is completely unnecessary.
- Clicking a node on the DB changes its size/color. Doesn't always reset properly afterward when you click away.
- Apparently if you click too many times, it stops letting you click on nodes because of some variable called `tog` in `viz-d3.js` (around line 681, I think).
- People changing their names on Facebook will cause everyone who was friends with them to fail. Maybe add a check/exception for people who don't exist anymore.
- Sometimes the "direction" of interactions is backwards (i.e. "A liked B's photo" when it was A's photo).

# TODO
- Make accounts information file and put in user folder.

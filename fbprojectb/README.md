TrueFriend
==========
Lehigh University DAS Lab and Cornell Interaction Design Lab<br>
Professor Eric Baumer<br>
https://das-lab.org/truefriend<br>
https://github.com/ericpsb/Research/tree/master/fbprojectb

Last updated: August 3, 2017 by Peter Schaedler (pwschaedler@gmail.com)

## Overview
TrueFriend is a website/Facebook app that infers the degrees of friendship between people based on the frequency of online interactions, and thus finds the "true friends" of a user. By using the Facebook Graph API, TrueFriend requests every item in a user's feed and stores it in a MongoDB database. From there, Python scripts process the information into two representations: 1) individual interactions, such as comments, which include the users involved and the posts from which they were gathered, and 2) JSON to represent the nodes and links that will be loaded into a D3.js force-directed graph. Each node represents a person on Facebook, and two nodes are connected if there is some interaction between them on the user's timeline. The more they interact, the closer the nodes will be.

## Software Architecture
The program consists mainly of three parts: front-end HTML, JavaScript, and PHP; back-end PHP scripts; and back-end Python scripts.

### Program Flow
When the user nagivates to https://das-lab.org/truefriend, they will arrive at `index.php`, where they can log into Facebook. From there, they will be redirected to `callback.php`, which has PHP code to run `ltget.py` on the server. From here, the user can click "Proceed to Visualization" and go to `initViz.php` which gives some basic statistics about the user's Facebook account. When the visualization has been generated, they will then be able to go to `viz.php`, which shows the full force-directed graph. In the background, `ltget.py` calls `update_db_v4.py`, which in turn makes use of `viz_generator.py`.

### Description of Individual Files
#### Front-End


#### Back-End PHP


#### Back-End Python


#### Old Files
There is a folder called `unused_old_files`. Technically, these files should just be deleted, since they don't affect the program whatsoever. But for convenience and because I'm a code hoarder, I've placed these files in a folder to keep them out of the way.

### Database Information


### Requirements and Necessary Python Modules


## Accounts and Related Information
See Peter's user account on Saiph for this information.

## Known Issues

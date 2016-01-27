# notifywait script by vmhacks.com

#so this is the main shit, super simple one line
# -e are the events were checking for, -mrq means monitor, recursive, quiet
# --format says that we want it to just return directory (w) and filename (f)
# /root/secretPorn is the folder we’re watching
# –excludei means we’re ignoring case and skipping any files that match the regex string
# we then pipe any output to a while loop
echo "watcher started"
/usr/bin/inotifywait -e create,delete,modify,move -mrq --format %w%f ./longtermaccesstoken.txt --excludei sess_* | while read INPUT;
do
echo "watcher event"
# Get the directory name
DIRECTORY=`/usr/bin/dirname $INPUT`

# Get the filename
FILENAME=`basename $INPUT`

# Replace spaces in file names in case you want to send output to HTTP
HTTPFINAL=`/bin/echo $INPUT | /bin/sed -e 's/ /%20/g'`

# Get the current date

DATE=`date`

# Do stuff with this info
echo "THE FILE $DIRECTORY/$FILENAME WAS CHANGED AT $DATE"
echo " "
#echo "Pass this info to be processed by PHP file through HTTP"
#echo "running curl http://localhost/files.php?file=$HTTPFINAL"
#/usr/bin/curl "http://localhost/files.php?file=$HTTPFINAL"

echo "Running ltget.py ..."

#running ltget.py
#python ltget.py
#python initViz.py


#updating database 
#python update_db_v4.py &
python update_db_v4.py
#python newViz.py
done


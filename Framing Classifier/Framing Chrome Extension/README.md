# Article Framing Plugin, made by Alex Van Heest #

This plugin allows Chrome users to quickly determine the different kinds of framing in any article they're reading.

When run on an HTTP/S page, the plugin takes the HTML, finds the article content, and sends it to a Flask backend as a JSON. The JSON will contain the URL and the contents of the article. Flask will process the text of the article and return the framing of the article via the plugin. Finally, the plugin will display framing results from the preexisting Python classifiers.

# Running This Using a Local Flask Instance #

To run this using a local Flask instance:
1. In the Chrome Extensions menu, load from file or click Reload on the Framing Classifier plugin to get the latest version.
2. In the Flask directory, run "python run.py" to launch the Flask instance.
3. Open a page with a news article in Chrome.
4. Click the Framing Classifier Extension logo (a frame). It will take a second before highlighting and displaying results.
5. Now check the Terminal window where the Flask instance is running. The article URL and contents should be displayed in a received JSON object.

# Beyond the Local Flask Instance #

All that should need to be changed to make this run non-locally is:
* any references to localhost or 127.0.0.1 in the popup.js file
* any references to localhost or 127.0.0.1 in the manifest.json file should be changed to the API url

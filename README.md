# Playbrush coding test

## About this task

Details about the requirements can be found in `Software Developer Task.pdf`.

## Prerequisites
Modules to be installed:
In addition to Python 3.6.2, please see requirements.txt

Untested on other versions. Try at your own peril.

## How to start and use the application

### Direct output option
Run the file `brush_info.py` as normal python script to create a `output.csv` in the project root folder that
contains all user data. The console log will show very basic group analytics data.

### Webview option
Either start flask as usual or plainly run 'routes.py' for a graphical version.

`http://localhost:5000/` will show a basic group analytics and user analytics table.


## Suggested improvements
* Vet against bad data in input (like typos and other shenanigans in input CSVs)
* Outputs have been manually spot-checked for correctness. Could do with some unittests.
* Pandas or similar libraries could do wonders for data wrangling. Might save quite a few lines of code.
* Make the input more variable (upload csv files via the web browser)
* Use Argparse to allow easy command line access to alternative file-routes
* Beef up graphical representation
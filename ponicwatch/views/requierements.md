Python Packages
===============

APScheduler
-----------
https://apscheduler.readthedocs.io/en/latest/
Heart of this program --> principal function of the controller

Bottle
------
https://bottlepy.org/docs/dev/
View of the program to allow remote monitoring.

MarkDown
--------
https://pythonhosted.org/Markdown/index.html
Simply used to render the MarkDown documents into HTML for populating the Bottle /docs pages
Note: the .md files should be in the /views/ sub-folder

MatPlotLib
----------
http://matplotlib.org/
To create the plots/graphics images embeded in the HTML pages.
Note: images will be .PNG generated in the /images/ sub-folder

bottlesession
-------------
https://github.com/linsomniac/bottlesession
Atttention:

                #  save off a secret to a tmp file
                secret = ''.join([
                    random.choice(string.ascii_letters)   #  <-- modification on line 172
                    for x in range(32)])

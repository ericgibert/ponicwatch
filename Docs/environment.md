Environment and Setups
======================

Python 3
--------

On the development: Python 3.4.2 --> now 3.5.3

````bash
    sudo pip3 install virtualenvwrapper
    mkvirtualenv -p python3 ponicwatch
    workon ponicwatch
````

````python
>>> sqlite3.version
'2.6.0'
````


pip install bottle
````python
>>> bottle.__version__
'0.12.13'
````

Sqlite
------

GUI: dnf install sqliteman

APScheduler
-----------
In-process task scheduler with Cron-like capabilities

https://pypi.python.org/pypi/APScheduler/

    pip install apscheduler
    
Markdown
--------

Python Markdown converts Markdown to HTML  and is used in the http_view module to reender the *.md files.

See <https://pythonhosted.org/Markdown/> for more
information and instructions on how to extend the functionality of
Python Markdown.

    pip install markdown
    >>> markdown.version
    2.6.9

For electronic
--------------
- smbus  / alternative wiringpi2: http://raspi.tv/2013/using-the-mcp23017-port-expander-with-wiringpi2-to-give-you-16-new-gpio-ports-part-3#top
- gpiozero
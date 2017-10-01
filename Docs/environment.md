Environment and Setups on Raspberry Pi 3
========================================

Python 3
--------

On "RASPBIAN STRETCH WITH DESKTOP" : Python 3.5.3

````bash
    sudo pip3 install virtualenvwrapper
    mkvirtualenv -p python3 ponicwatch
    workon ponicwatch
````

````python
>>> sqlite3.version
'2.6.0'
````

Bottle and Bottle-Session
-------------------------

####bottle
Used to provide the HTTP server to interract with the application

pip install bottle
````python
>>> bottle.__version__
'0.12.13'
````

####bottle-session
Install using either pip or easy_install:

    $ pip install bottle-session

or you can download the latest version from bitbucket:

    $ git clone https://devries@bitbucket.org/devries/bottle-session.git
    $ cd bottle-session
    $ python setup.py install



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


Matplotlib
----------

I tried `pip install matplotlib` without success: error in compilation.
Plan B:
```bash
    sudo apt-get python3-matplotlib
    toggleglobalsitepackages
```
This latest command allows the virtual environment to benefit for the global site-packages.

```bash
    >>> import matplotlib
    >>> matplotlib.__version__
    '2.0.0'
```
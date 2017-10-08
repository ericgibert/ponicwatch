Environment and Setups on Raspberry Pi 3
========================================

Python 3
--------

On "RASPBIAN STRETCH WITH DESKTOP" : Python 3.5.3

Add two lines at the end of .bashrc:
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME


````bash
    sudo apt-get install virtualenvwrapper
    mkvirtualenv -p /usr/bin/python3 ponicwatch
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

####bottlesession
````bash
	cd ponicwatch
	mkdir Private
	cd Private
	git clone https://github.com/linsomniac/bottlesession
````
 
Attention: Edit with `nano bottlesession/bottlesession.py` its line 172 ^_
```python
        #  save off a secret to a tmp file
        secret = ''.join([
            random.choice(string.ascii_letters)   #  <-- modification on line 172
            for x in range(32)])
```

then `cp bottlesession.py ~/.virtualenvs/ponicwatch/lib/python3.5/site-packages/`


Sqlite
------

GUI: sudo apt-get install sqlitebrowser

APScheduler
-----------
In-process task scheduler with Cron-like capabilities

https://pypi.python.org/pypi/APScheduler/

    pip install apscheduler
	>>> apscheduler.__version__
	'3.3.1'

    
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
    sudo apt-get install python3-matplotlib
    toggleglobalsitepackages
```
This latest command allows the virtual environment to benefit for the global site-packages.

```bash
    >>> import matplotlib
    >>> matplotlib.__version__
    '2.0.0'
```

Ponicwatch
----------

git clone https://github.com/ericgibert/ponicwatch

git config --global user.name "ericgibert@yahoo.fr"
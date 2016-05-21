Environment and Setups
======================

Python 3
--------

On the development: Python 3.4.2

mkvirtualenv -p python3 ponicwatch

workon ponicwatch
>>> sqlite3.version
'2.6.0'

pip install bottle

>>> bottle.__version__
'0.12.9'


Sqlite
------

GUI: dnf install sqliteman



For electronic:
- smbus  / alternative wiringpi2: http://raspi.tv/2013/using-the-mcp23017-port-expander-with-wiringpi2-to-give-you-16-new-gpio-ports-part-3#top
- gpiozero

PonicWatch Architecture
=======================

1) Controller
-------------

The Controller is a Python3 application running on a PC/Raspi whose tasks are:
- monitor various sensors and log their data in a database
    * temperature
    * EC
    * pH
    
- activate switches based on a schedule
    * pump
    * light
    

2) Webs server
--------------

A light web server based on Bottle allows interaction with the database.
Various webservices expose the data logged by the Controller.
Setting up of the Controller's parameters is also possible but restricted in access.

3) Data visualization
---------------------

A set of HMTL5/js/css files offer to display the data logged by the Controller.
Futhermore, using Cordova, some of the pages will be converted into an Android application.

4) Database
-----------

On the Controller device, Sqlite is used. A synchronization will be exectuted with a MySQL database in the cloud for remote access by the Android application "on the go".



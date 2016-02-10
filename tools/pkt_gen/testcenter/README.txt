################################################
Instructions on using Spirent Testcenter Scripts
################################################

The user has two different options to work with Spirent TestCenter. Depending on the option, the user has to select right set of files 

Option-1: Using the Spirent TestCenter command sequencer.
With this option the user should have the spirent testcenter application installed and running locally on the system. 

Option-2: Using the REST client package 
The stcrestclient package provides the stchttp.py ReST API wrapper module.  This allows simple function calls, nearly identical to those provided by StcPython.py, to be used to access TestCenter server sessions via the STC ReST API. Basic ReST functionality is provided by the resthttp module, and may be used for writing ReST clients independent of STC.
- Project page: <https://github.com/Spirent/py-stcrestclient>
- Package download: <http://pypi.python.org/pypi/stcrestclient>


With the first option, the user can select one of the following files:
1. testcenter-rfc2544-throughput.py

Whereas, with the second option the user can select any of the following files:
1. testcenter-rfc2544-rest-throughtput.py
2. testcenter-rfc2544-rest-backtoback.py
3. testcenter-rfc2544-rest-frameloss.py
4. testcenter-rfc2455-rest-latency.py


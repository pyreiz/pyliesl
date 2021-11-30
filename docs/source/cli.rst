liesl CLI
---------

   
liesl also offers a command line interface. This interface can be accessed after installation of the package from the terminal, e.g. create a mock LSL outlet producing fake EEG with    

.. code-block:: bash

   liesl mock --type EEG

liesl
~~~~~
.. code-block:: none

   usage: liesl [-h] {config,list,show,mock,xdf} ...
   
   positional arguments:
     {config,list,show,mock,xdf}
       config              initialize the lsl_api.cfg for all users with system,
                           globally for this user with global or locally in this
                           folder with local
       list                list available LSL streams
       show                Visualize a specific LSL streams
       mock                mock a LSL stream
       xdf                 inspect an XDF file
   
   optional arguments:
     -h, --help            show this help message and exit


liesl config
~~~~~~~~~~~~
.. code-block:: none

   usage: liesl config [-h] [--default] [--sessionid SESSIONID]
                       [--knownpeers KNOWNPEERS]
                       {system,user,local}
   
   positional arguments:
     {system,user,local}   system: /etc/lsl_api/lsl_api.cfg or
                           C:\etc\lsl_api\lsl_api.cfg on Windows. user:
                           ~/lsl_api/lsl_api.cfg or
                           C:\Users\username\lsl_api\lsl_api.cfg on Windows.
                           local: lsl_api.cfg in the current working directory
   
   optional arguments:
     -h, --help            show this help message and exit
     --default             initializes a configuration from default
     --sessionid SESSIONID
                           sets the sessionid for this level
     --knownpeers KNOWNPEERS
                           set knownpeers for this level


liesl list
~~~~~~~~~~
.. code-block:: none

   usage: liesl list [-h] [--field FIELD]
   
   optional arguments:
     -h, --help     show this help message and exit
     --field FIELD  which field to print


liesl show
~~~~~~~~~~
.. code-block:: none

   usage: liesl show [-h] [--name NAME] [--type TYPE] [--channel CHANNEL]
                     [--backend {mpl,ascii}] [--frate FRATE]
   
   optional arguments:
     -h, --help            show this help message and exit
     --name NAME           name of the stream
     --type TYPE           type of the stream
     --channel CHANNEL     which channel to visualize
     --backend {mpl,ascii}
                           what backend to use
     --frate FRATE         at which frequency the plot will be updated


liesl mock
~~~~~~~~~~
.. code-block:: none

   usage: liesl mock [-h] [--type TYPE]
   
   optional arguments:
     -h, --help   show this help message and exit
     --type TYPE  type of the stream
     --file FILE  File that will be used as mock data


liesl xdf
~~~~~~~~~
.. code-block:: none

   usage: liesl xdf [-h] [-a AT_MOST] [-t TIMEOUT] filename
   
   positional arguments:
     filename              filename
   
   optional arguments:
     -h, --help            show this help message and exit
     -a AT_MOST, --at-most AT_MOST
                           return latest once that many streams were found,
                           regardless of how long it takes. Useful if file is
                           very large, and can prevent parsing the whole file.
                           defaults to sys.maxsize because integers are required,
                           but unbound in python. Set it to 0' to load the file
                           completely
     -t TIMEOUT, --timeout TIMEOUT
                           return latest after this many seconds, regardless of
                           how many streams were found. Useful if the file is
                           very large, and you are sure you started recording all
                           streams at the beginning, as this prevents parsing
                           the whole file. defaults to 1 second. Set it to 'inf'
                           to load the file completely



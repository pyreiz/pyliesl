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


liesl xdf
~~~~~~~~~
.. code-block:: none

   usage: liesl xdf [-h] [--at-most AT_MOST] filename
   
   positional arguments:
     filename           filename
   
   optional arguments:
     -h, --help         show this help message and exit
     --at-most AT_MOST  only peek into the file, looking for at most N
                        streaminfos. If searching takes too long, returns after a
                        certain time anyways. Useful for example if file is very
                        large, and you are sure you started recording all streams
                        at the beginnging, as this prevents parsing the whole
                        file



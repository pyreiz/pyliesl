### LieSL

is a repository adding several convenient tools to LSL
(https://pypi.org/project/pylsl/) and to inspect xdf files.

These are accessible through the terminal, e.g. 
```{bash}
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
```

### liesl config

creates configuration files (lsl_api.cfg) for solving issues with
[network connectivity](https://github.com/sccn/labstreaminglayer/wiki/NetworkConnectivity#configuration-file-locations)
```
usage: liesl config [-h] [--default] {global,system,local}

positional arguments:
  {global,system,local}
                        system: /etc/lsl_api/lsl_api.cfg or
                        C:\etc\lsl_api\lsl_api.cfg on Windows. global:
                        ~/lsl_api/lsl_api.cfg or
                        C:\Users\username\lsl_api\lsl_api.cfg on Windows.
                        local: lsl_api.cfg in the current working directory

optional arguments:
  -h, --help            show this help message and exit
  --default             initializes a configuration from default
```


### liesl mock
```
usage: liesl mock [-h] [--name NAME] [--type TYPE]
                  [--channel_count CHANNEL_COUNT]

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           name of the stream
  --type TYPE           type of the stream
  --channel_count CHANNEL_COUNT
                        number of channels
```


### liesl xdf
```
usage: liesl xdf [-h] filename

positional arguments:
  filename    filename

optional arguments:
  -h, --help  show this help message and exit
```
###### Example
in bash, run `git clone https://github.com/xdf-modules/example-files.git` to
download the example files from the xdf repository. Then, `cd example-files`,
and run `liesl xdf minimal.xdf` to receive the following printout
```{bash}
Loading minimal.xdf

                                                             XDF Fileversion 1.0

Name                             Type        Ch   Fs                      Source
--------------------------------------------------------------------------------
SendDataC                        EEG         3    10                          ""
SendDataString               StringMarker    1    10                          ""


SendDataC                                                         Exemplary data
--------------------------------------------------------------------------------
─────────╮                                                                      
         │                                                                      
         │                                                                      
         │                                                                      
         │                                                                      
         │                                                                      
         │                                                                      
         │                                                                      
         │                                                                      
         ╰──────────────────────────────────────────────────────────────────────
5                                     5.4                                    5.8

SendDataString                                                            Events
--------------------------------------------------------------------------------
<?xml version="1.0"?><info><writer>LabRecorder...                              1
Hello                                                                          2
World                                                                          2
from                                                                           2
LSL                                                                            2

Overview finished for minimal.xdf
```
### Caveat
This should not be considered a stable repository, and i currently am 
tweaking a lot to fit specific needs.

# LieSL

is a repository with several convenient tools to manage and test LSL (<https://pypi.org/project/pylsl/>) and to inspect xdf files.

These are accessible through the terminal, e.g.

```
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

## Installation

From the terminal,

```bash
git clone https://github.com/pyreiz/pyliesl.git
cd pyliesl
pip install -r requirements.txt
pip install -e .
```

after these steps, the command line interface should be detectable from your path.

--------------------------------------------------------------------------------

## liesl config

creates configuration files (lsl_api.cfg) for solving issues with [network connectivity](https://github.com/sccn/labstreaminglayer/wiki/NetworkConnectivity#configuration-file-locations)

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

### Example

From the terminal, run `liesl config user --default` to create a default configuratin file for lsl on the user level. (see <https://github.com/sccn/labstreaminglayer/wiki/NetworkConnectivity#configuration-file-locations> for more details). You can then change the session id with `liesl config user --sessionid test` and add the localhost to knownpeers `liesl config user --knownpeers 127.0.0.1`. Afterwards, lsl config user returns

```javascript
'lab': {'KnownPeers': '{127.0.0.1}', 'SessionID': 'test'},
 'multicast': {'AddressesOverride': '{}',
               'GlobalAddresses': '{}',
               'LinkAddresses': '{255.255.255.255, 224.0.0.183, '
                                'FF02:113D:6FDD:2C17:A643:FFE2:1BD1:3CD2}',
               'MachineAddresses': '{FF31:113D:6FDD:2C17:A643:FFE2:1BD1:3CD2}',
               'OrganizationAddresses': '{239.192.172.215, '
                                        'FF08:113D:6FDD:2C17:A643:FFE2:1BD1:3CD2}',
               'ResolveScope': 'site',
               'SiteAddresses': '{239.255.172.215, '
                                'FF05:113D:6FDD:2C17:A643:FFE2:1BD1:3CD2}',
               'TTLOverride': '-1'},
 'ports': {'BasePort': '16572',
           'IPv6': 'allow',
           'MulticastPort': '16571',
           'PortRange': '32'}}
```

--------------------------------------------------------------------------------

## liesl mock

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

### Example

From the terminal, run `liesl mock` to create the default EEG stream with 8 channels and sampling rate of 100 Hz (similar to <https://github.com/labstreaminglayer/liblsl-Python/blob/master/pylsl/examples/SendData.py>)

```xml
<info>
    <name>Liesl-Mock</name>
    <type>EEG</type>
    <channel_count>8</channel_count>
    <nominal_srate>100</nominal_srate>
    <channel_format>float32</channel_format>
    <source_id>8781768652457</source_id>
    <version>1.1000000000000001</version>
    <created_at>0</created_at>
    <uid></uid>
    <session_id></session_id>
    <hostname></hostname>
    <v4address></v4address>
    <v4data_port>0</v4data_port>
    <v4service_port>0</v4service_port>
    <v6address></v6address>
    <v6data_port>0</v6data_port>
    <v6service_port>0</v6service_port>
    <desc>
        <channels>
            <channel>
                <label>C001</label>
                <unit>au</unit>
                <type>MockEEG</type>
            </channel>
            <channel>
                <label>C002</label>
                <unit>au</unit>
                <type>MockEEG</type>
            </channel>
            <channel>
                <label>C003</label>
                <unit>au</unit>
                <type>MockEEG</type>
            </channel>
            <channel>
                <label>C004</label>
                <unit>au</unit>
                <type>MockEEG</type>
            </channel>
            <channel>
                <label>C005</label>
                <unit>au</unit>
                <type>MockEEG</type>
            </channel>
            <channel>
                <label>C006</label>
                <unit>au</unit>
                <type>MockEEG</type>
            </channel>
            <channel>
                <label>C007</label>
                <unit>au</unit>
                <type>MockEEG</type>
            </channel>
        </channels>
    </desc>
</info>


now sending data...
```

You can also start a mock marker stream with `liesl mock --type Marker`.

## liesl show

```
usage: liesl show [-h] [--name NAME] [--type TYPE] [--channel CHANNEL]
                  [--backend {mpl,textplot,reizbar}]

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           name of the stream
  --type TYPE           type of the stream
  --channel CHANNEL     which channel to visualize
  --backend {mpl,textplot,reizbar}
                        what backend to use
```

### Example

After starting a mock stream with `liesl mock`, you can visualize it in another terminal with e.g. `liesl show --channel 1`, returning

```
+1.0 |         ...... ......                                                    
     |      ...             ...                                                 
     |   ...                   ...                                              
     | ..                         ..                                            
     |                              ..                                          
     |                                \                                         
     |                                 ..                                       
     |                                   ..                                     
 0.0 | ------------------------------------..-----------------------------------
     |                                       \                                  
     |                                        ..                                
     |                                          \                               
     |                                           ..                             
     |                                             ..                           
     |                                               ..                        /
     |                                                 ...                   .. 
     |                                                    ..              ...   
-1.0 |                                                      ..............      
    27889.5                      27889.9                             27890.3
```

### liesl list

```
usage: liesl list [-h] [--field FIELD]

optional arguments: -h, --help show this help message and exit --field FIELD which field to print
```

#### Example

From the terminal, first start a mock stream with `liesl mock --type EEG`. In a second terminal, run `liesl list` to return

```xml
<?xml version="1.0"?>

<info><name>Liesl-Mock</name>
    <type>Marker</type>
    <channel_count>1</channel_count>
    <nominal_srate>0</nominal_srate>
    <channel_format>string</channel_format>
    <source_id>8746345783361</source_id>
    <version>1.1000000000000001</version>
    <created_at>2460.5402053009998</created_at>
    <uid>c1dabe64-368f-4c1e-8cb1-646eb3aee3b6</uid>
    <session_id>test</session_id>
    <hostname>rgugg-ThinkPad-X240</hostname>
    <v4address><v4data_port>16574</v4data_port>
    <v4service_port>16574</v4service_port>
    <v6address><v6data_port>16575</v6data_port>
    <v6service_port>16575</v6service_port>
    <desc>
</desc></v6address></v4address></info>
```

You can limit the report e.g. to the source_id by `liesl list --field source_id`, which would only return

```
8746345783361
```

--------------------------------------------------------------------------------

### liesl xdf

```
usage: liesl xdf [-h] filename

positional arguments: filename filename

optional arguments: -h, --help show this help message and exit
`
```

#### Example

From the terminal, run `git clone https://github.com/xdf-modules/example-files.git` to download the example files from the xdf repository. Then, `cd example-files`, and run `liesl xdf minimal.xdf` to receive the following printout

```
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
`
```

### Caveat

This should not be considered a stable repository, and i currently am tweaking a lot to fit specific needs.

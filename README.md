### MBTools
___

GUI Python application for reading and displaying modbus data from several sources.

Requirements:
- Python 3.6
- PyQt5
- pymodbus
- numpy

Implemented modules:
- Modbus driver (src/drivers/modbus);
- OIServer (src/oiserver);
- JSonServer (src/jsonserver) - not implemented ;

Tools:
- ModbusViewer - GUI application for observering modbus driver.
![](doc/screens/screen1.png)

___
### How to create virtual environment
**Windows**
~~~bash
$ python -m venv env
$ source env/Scripts/activate
(env)$ python -m pip install --upgrade pip
(env)$ pip install -r requirements.txt
#(env)$ pip install PyQt5 pymodbus numpy pyinstaller
(env)$ deactivate
~~~
**Linux**
~~~bash
$ python3 -m venv env
$ source env/bin/activate
(env)$ python -m pip install --upgrade pip
(env)$ pip install -r requirements.txt
#(env)$ pip install PyQt5 pymodbus numpy pyinstaller
(env)$ deactivate
~~~
___
### Packaging
**Windows**
~~~bash
$ source env/Scripts/activate
(env)$ python setup.py sdist
(env)$ deactivate
~~~
**Linux**
~~~bash
$ source env/bin/activate
(env)$ python setup.py sdist
(env)$ deactivate
~~~
Package **MDViewer-0.1.0.tar.gz** will be found in **dist** directory

___
#### Executable file creation
**Windows** (mdviewer.exe)
~~~bash
$ source env/Scripts/activate
(env)$ pyinstaller --clean --onefile --noconsole --icon=myico.ico --name mdviewer MBTools/main.py
(env)$ deactivate
$ cp -r MBTools/config/ dist/
~~~
**Linux**
~~~bash
$ source env/bin/activate
(env)$ pyinstaller --clean --onefile --noconsole --icon=myico.ico --name mdviewer MBTools/main.py
(env)$ deactivate
$ cp -r MBTools/config/ dist/  # optionally
~~~
Default configuration (**conf.json**) is located in **config** folder.:
~~~
$ tree.exe
.
├── MDViewer-0.1.0.tar.gz
├── config
│   ├── __init__.py
│   ├── conf.json
│   └── qss.css
└── mdviewer.exe
~~~
**conf.json** example:
~~~
{
  "devices": [
    { "name": "dev1", "protocol": "modbus", "ip": "127.0.0.1", "port": 502 }
  ],

  "tags": [
    {"name": "TAG1_REAL", "type": "REAL", "device": "dev1", "address": 100, "comment" : "Tag1 Real Type" },
    {"name": "TAG1_WORD", "type": "WORD", "device": "dev1", "address": 102, "comment" : "Tag2 WORD Type" }
  ]
}
~~~

---
### How to use
#### Installing requirements and MDViewer package
**Windows**
~~~bash
$ python3 -m venv env
$ source env/bin/activate
(env)$ python -m pip install --upgrade pip
(env)$ pip install PyQt5 pymodbus numpy pyinstaller
(env)$ pip install ../dist/MBTools-0.1.0.tar.gz
(env)$ deactivate
~~~
**Linux**
~~~bash
$ python -m venv env
$ source env/Scripts/activate
(env)$ python -m pip install --upgrade pip
(env)$ pip install PyQt5 pymodbus numpy pyinstaller
(env)$ pip install ../dist/MBTools-0.1.0.tar.gz
(env)$ deactivate
~~~
#### Example of using

~~~python
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from MBTools.oiserver.OIServer import IOServer
from MBTools.oiserver.OIServerConfigure import create_config, FormatName
import MBTools.oiserver.tools.OIServerViewer.OIServerViewer as oiv


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    # Server
    io = IOServer()

    # Server configuration
    conf = create_config(FormatName.JSON, "../MBTools/config/conf.json")
    io.set_config(conf)

    # Server tag viewer
    oiviewer = oiv.OIServerViewer()
    oiviewer.setOiServer(io)
    oiviewer.show()

    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))
~~~

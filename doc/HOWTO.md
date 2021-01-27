### HOWTO 
___

### How to deploy application
1. Script configuring:
    set path for project root directory in src/drivers/modbus/main.py: 
    **sys.path.append(ModbusViewer)**
    
2. Creating virtual environment using venv module:
    ```bash
   $ cd ModbusViewer
   $ python3 -m venv env
    ```
3. Installing dependencies:
    ```bash
   $ source env/bin/activate
   $ pip install PyQt5 pymodbus numpy
    ```
4. Executing the script:
    ```bash
   $ MBTools/driver/modbus/main.py
    ```
5. At the end:
    ```bash
   $ deactivate
    ```


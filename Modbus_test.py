import logging
import threading
import time
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

# Configure logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Define the data storage
# We'll use SequentialDataBlock for simplicity.
# Address 0 to 99 for holding registers (hr)
holding_registers = ModbusSequentialDataBlock(0, [0]*100)

# what is a Modbus slave context and how does this relate to unit IDs?

# Create the Modbus slave context (unit ID 1)
# You can add coils (c), discrete inputs (di), and input registers (ir) similarly
slave_context = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0]*100),
    co=ModbusSequentialDataBlock(0, [0]*100),
    hr=holding_registers,
    ir=ModbusSequentialDataBlock(0, [0]*100))

# Create the overall server context with the slave context
context = ModbusServerContext(slaves=slave_context, single=True)

# Create device identification
identity = ModbusDeviceIdentification()
identity.VendorName = 'Raspberry Pi'
identity.ProductCode = 'RPi5'
identity.VendorUrl = '[https://www.raspberrypi.com](https://www.raspberrypi.com)'
identity.ProductName = 'Modbus Server'

# Set some initial values
holding_registers.setValues(0, [1000])      # Address 0 = 1000
holding_registers.setValues(1, [2000])      # Address 1 = 2000
holding_registers.setValues(10, [100, 200, 300])  # Addresses 10-12

# Start the server
if __name__ == "__main__":
    # Start server in background thread
    server_thread = threading.Thread(
        target=StartTcpServer,
        kwargs={'context': context, 'identity': identity, 'address': ("0.0.0.0", 5020)},
        daemon=True
    )
    server_thread.start()
    print("Modbus server started on port 5020")
    
    # Update values in a loop
    counter = 0
    try:
        holding_registers.setValues(2, 1234)  # Example of setting a single value
        holding_registers.setValues(3, [10, 20, 30, 40, 50])  # Example of setting multiple values
        while True:
            # Update holding register at address 0 with incrementing counter
            holding_registers.setValues(0, [counter % 65536])
            
            # Update address 1 with timestamp
            holding_registers.setValues(1, [int(time.time()) % 65536])
            
            # Update addresses 10-12 with some varying values
            holding_registers.setValues(10, [counter % 100, (counter * 2) % 100, (counter * 3) % 100])
            
            print(f"Updated: counter={counter}, timestamp={int(time.time()) % 65536}")
            counter += 1
            time.sleep(1)  # Update every second
    except KeyboardInterrupt:
        print("\nServer stopped")

#Set values:

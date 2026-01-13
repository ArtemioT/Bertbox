#First attempt at establishing modbus connection without freezing the system

import asyncio
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import (
    ModbusSlaveContext, 
    ModbusServerContext,
    ModbusSequentialDataBlock,
)


store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*20)
)

context = ModbusServerContext(slaves=store, single=True)

async def sensor_task():
    while True:
        sensor_value = 42
        store.setValues(3, 1, [sensor_value])
        await asyncio.sleep(1)

async def main():
    print("Async Modbus TCP server running")
    await asyncio.gather(
        StartAsyncTcpServer(context, address=("0.0.0.0", 1502)),
        sensor_task(),
    )

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Shutting down")
    
    




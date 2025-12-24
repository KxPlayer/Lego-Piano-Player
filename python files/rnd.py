import socket, asyncio
from contextlib import suppress
from bleak import BleakScanner, BleakClient

# variables
PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"
HOST = 'localhost'
PORT = 5000
HUBS = ["Technic Hub 1", "Technic Hub 2"]
CLIENTS = set()


# set up connection to hubs
async def connect_hub(name, lock):
    def handle_disconnect(_):
        print("Hub was disconnected.")

        if not main_task.done():
            main_task.cancel()

    def handle_rx(_, data: bytearray):
        if data[0] == 0x01:  # "write stdout" event (0x01)
            payload = data[1:]

            if payload == b"rdy":
                ready_event.set()
            else:
                print("Received:", payload)

    main_task = asyncio.current_task()
    ready_event = asyncio.Event()

    async with lock:
        # Scan for hub and connect
        device = await BleakScanner.find_device_by_name(name)

        if device is None:
            print(f"could not find hub with name: {name}")
            return None

        print('found hub', name)

        await BleakClient(device, handle_disconnect).connect()

        return device


async def main():
    lock = asyncio.Lock()

    results = await asyncio.gather(
        *(
            connect_hub(hub, lock)
            for hub in HUBS
        )
    )

    print(results)

with suppress(asyncio.CancelledError):
    asyncio.run(main())

'''# set up server
server = socket.socket()
server.bind((HOST, PORT))
server.listen(1)
print("Waiting for connection...")
conn, addr = server.accept()
print("Connected by", addr)

# loop
while True:
    # reads from socket
    data = conn.recv(1024)
    if not data:
        break
    values = [int(value) for value in data.decode().split("\n") if value]

    print("Received:", values)

conn.close()
'''
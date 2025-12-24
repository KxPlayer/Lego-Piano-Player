import socket, asyncio
from contextlib import suppress
from bleak import BleakScanner, BleakClient

# variables
PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"
HOST = 'localhost'
PORT = 5000
#HUBS = ["Technic Hub 1", "Technic Hub 2"]
HUBS = ["Technic Hub 1"]


# set up connection to hubs
async def connect_hub(name, lock):
    def handle_disconnect(_):
        print("Hub was disconnected.")

        if not main_task.done():
            main_task.cancel()

    main_task = asyncio.current_task()

    async with lock:
        # Scan for hub and connect
        device = await BleakScanner.find_device_by_name(name)

        if device is None:
            print(f"could not find hub with name: {name}")
            return None

        print('found hub', name)

        client = BleakClient(device, handle_disconnect)

        await client.connect()

        return client


async def send_data(client):

    def handle_rx(_, data: bytearray):
        if data[0] == 0x01:  # "write stdout" event (0x01)
            payload = data[1:]

            if payload == b"rdy":
                ready_event.set()
            else:
                print("Received:", payload)

    ready_event = asyncio.Event()

    # Subscribe to notifications from the hub.
    await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)

    async def send(data):
        # Wait for hub to say that it is ready to receive data.
        await ready_event.wait()
        # Prepare for the next ready event.
        ready_event.clear()
        # Send the data to the hub.
        await client.write_gatt_char(
            PYBRICKS_COMMAND_EVENT_CHAR_UUID,
            b"\x06" + data,  # prepend "write stdin" command (0x06)
            response=True
        )

    # Tell user to start program on the hub.
    #
    print("Start the program on the hub now with the button.")

    passing_list = [-1, 1, -1, 1]

    # Send a few messages to the hub.
    for i in passing_list:
        await send(i.to_bytes(signed=True))
        await asyncio.sleep(1)

    # Send a message to indicate stop.
    await send((0).to_bytes())


async def main():
    lock = asyncio.Lock()

    return await asyncio.gather(
        *(
            connect_hub(hub, lock)
            for hub in HUBS
        )
    )

with suppress(asyncio.CancelledError):
    CLIENTS = asyncio.run(main())

    for client in CLIENTS:
        asyncio.run(send_data(client))

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
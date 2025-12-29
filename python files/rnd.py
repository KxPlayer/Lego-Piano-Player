import socket, asyncio
import threading
from contextlib import suppress
from bleak import BleakScanner, BleakClient

# variables
PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"
HOST = 'localhost'
PORT = 5000
#HUBS = ["Technic Hub 1", "Technic Hub 2"]
HUBS = ["Technic Hub 1"]
QUEUES = []


# set up connection to hubs
async def connect_hub(name, lock):
    def handle_disconnect(_):
        print("Hub was disconnected.")

        if not main_task.done():
            main_task.cancel()

    print("Searching for", name)

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


async def send_data(client, queue):

    def handle_rx(_, data: bytearray):
        if data[0] == 0x01:  # "write stdout" event (0x01)
            payload = data[1:]

            if payload == b"rdy":
                ready_event.set()
            else:
                print("Received:", payload)

    ready_event = asyncio.Event()

    if client is None:
        print("Client not found")
        return

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
    print("Press button on hub to start loop")

    while True:
        if len(queue) > 0:
            if isinstance(queue[0], list):
                for a in queue[0]:
                    #print("is list")
                    await send(a.to_bytes(signed=True))
            else:
                #print("is int")
                await send(queue[0].to_bytes(signed=True))

            del queue[0]


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
        if client is None:
            break

        new_queue = []
        QUEUES.append(new_queue)
        thread = threading.Thread(target=asyncio.run, args=(send_data(client, new_queue),))
        thread.start()

    # set up server
    server = socket.socket()
    server.bind((HOST, PORT))
    server.listen(1)
    print("Start MIDI reader script (should be done after hubs have buttons pressed)")

    conn, addr = server.accept()
    print("Connected by", addr)

    while True:
        # reads from socket
        data = conn.recv(1024)
        if not data:
            break
        values = [int(value) for value in data.decode().split("\n") if value]
        for q in QUEUES:
            q.append(values)

        print("Received:", values)


conn.close()

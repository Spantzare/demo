import asyncio
import platform
import sys
import time
import numpy as np

from bleak import BleakClient, BleakScanner

import streamlit as st

def make_grid(cols, rows):
    grid = [0] * cols
    for i in range(cols):
        with st.container():
            grid[i] = st.columns(rows)
    return grid
CHAR_UUID = "f0001132-0451-4000-b000-000000000000"
ADDRESS = (
   "80:6F:B0:1E:E0:94"
    if platform.system() != "Darwin"
    else "B9EA5233-37EF-4DD6-87A8-2A875E821C46"
)

#def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
#    """Simple notification handler which prints the data received."""
#    print(f"{data}")

async def run_ble_client(address: str, char_uuid: str, queue: asyncio.Queue):
    async def callback_handler(_, data):
        await queue.put((time.time(), data))

    async with BleakClient(address) as client:
        print(f"Connected: {client.is_connected}")
        await client.start_notify(char_uuid, callback_handler)
        await asyncio.sleep(5.0)
        await client.stop_notify(char_uuid)
        # Send an "exit command to the consumer"
        await queue.put((time.time(), None))

async def run_queue_consumer(queue: asyncio.Queue):
    while True:
        # Use await asyncio.wait_for(queue.get(), timeout=1.0) if you want a timeout for getting data.
        epoch, data = await queue.get()
        if data is None:
            print(
                "Got message from client about disconnection. Exiting consumer loop..."
            )
            break
        else:
            print(f"Received callback data via async queue at {epoch}: {data}")

async def run_queue_consumer(queue: asyncio.Queue):
    while True:
        # Use await asyncio.wait_for(queue.get(), timeout=1.0) if you want a timeout for getting data.
        epoch, data = await queue.get()
        if data is None:
            print(
                "Got message from client about disconnection. Exiting consumer loop..."
            )
            break
        else:
            print(f"Received callback data via async queue at {epoch}: {data}")


async def main():
    st.set_page_config(page_title="RISE PEA Demos", page_icon="Fire")
    st.title("RISE Printed Electronics Arena Demonstrator")

    if st.button('Connect to Bluetooth Device'):
        device = await BleakScanner.find_device_by_address(ADDRESS, timeout=5.0)
        if device:
            queue = asyncio.Queue()
            client_task = run_ble_client(ADDRESS, CHAR_UUID, queue)
            consumer_task = run_queue_consumer(queue)
            await asyncio.gather(client_task, consumer_task)

            st.write('Connected')
        else:
            st.write('No device found')
        
        option = st.selectbox(
            'Choose Device',
            ('Email', 'Home phone', 'Mobile phone'))

        st.write('You selected:', option)

    grid = make_grid(2, 2)

    async def hoof_sim(title, widget):
        last_rows = np.random.randn(1, 1)
        widget.write(title)
        chart = widget.line_chart(last_rows)

        for i in range(1, 101):
            new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
            chart.add_rows(new_rows)
            last_rows = new_rows
            await asyncio.sleep(0.05)

    if st.button('Plot Graphs'):
        await asyncio.gather(
            hoof_sim("Front left", grid[0][0]),
            hoof_sim("Front right", grid[0][1]),
            hoof_sim("Rear left", grid[1][0]),
            hoof_sim("Rear right", grid[1][1]),
        )

    st.button("Re-run")

    if st.button('Say hello'):
        st.write('Why hello there')
    else:
        st.write('Goodbye')
    
    st.download_button(
    label="DOWNLOAD!",
    data="trees",
    file_name="string.txt",
    mime="text/plain"
)
    
loop = asyncio.new_event_loop()
loop.run_until_complete(main())
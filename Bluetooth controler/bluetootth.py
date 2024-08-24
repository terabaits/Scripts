import asyncio
import sounddevice as sd
import numpy as np
from bleak import BleakClient

deviceUUIDs = ["D6:ED:E1:07:45:C2", "E6:20:C9:EF:66:AD"]
sendCharUuid = 'f000aa61-0451-4000-b000-000000000000'

async def set_color(client, r, g, b):
    command = bytearray([0xae, 0xa1, r, g, b, 0x56])
    await client.write_gatt_char(sendCharUuid, command, response=True)

async def main():
    # Connect to all clients
    clients = [await BleakClient(uuid).connect() for uuid in deviceUUIDs]

    async def audio_loop():
        # Audio callback within asyncio context
        def audio_callback(indata, frames, time, status):
            audio_data = np.abs(np.fft.rfft(indata[:, 0]))  # Mono channel FFT
            volume_norm = np.linalg.norm(audio_data) * 10
            brightness = int(min(max(volume_norm, 0), 255))  # Scale to 0-255

            # Update colors asynchronously
            for i, client in enumerate(clients):
                asyncio.run_coroutine_threadsafe(
                    set_color(client, brightness if i == 0 else 0, brightness if i == 1 else 0, 0),
                    loop
                )

        # Start audio stream
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=44100):
            await asyncio.sleep(10)  # Keep running for 10 seconds

    # Run the audio loop
    loop = asyncio.get_event_loop()
    await audio_loop()

    # Disconnect clients
    for client in clients:
        await client.disconnect()

# Run the main function
asyncio.run(main())

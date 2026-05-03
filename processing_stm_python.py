import serial
import time
import wave
import numpy as np

# Setup
port = "COM4"
baud = 115200
sample_rate = 12000
duration = int(input("How many seconds of audio to record? "))
total_samples = duration * sample_rate
audio = []
ser = serial.Serial(port, baud, timeout=5)



# Optimization: Read the entire block at once rather than byte-by-byte

def read_data(duration):
    print(f"Recording {duration} seconds...")
    time.sleep(1) # Give the port time to initialize
    ser.reset_input_buffer()
    for  i in range(total_samples):
        raw_data = ser.read(size=1)
        if raw_data:
            audio.append(raw_data[0])

    if len(raw_data) < total_samples:
        print(f"Warning: Only captured {len(raw_data)} samples.")
    data = np.array(audio)
    data = (data-data.min())/data.max()
    data = data*255
    data = data.astype(np.uint8)
    return data

def export_wav(data:np.array):
    # Export to WAV
    with wave.open('output.wav', 'wb') as wf:
        wf.setnchannels(1)      # Mono
        wf.setsampwidth(1)      # 8-bit (1 byte per sample)
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())

    print("Done! Saved to output.wav")

menu = """---RECORDING MODE SELECT---
Manual (m)
Distance Triggered (d)
Awaiting input: """

while(1):
    recording_mode = input(menu)
    if recording_mode == "d" or recording_mode == "m":
        break
    print("\nInvalid input, please input m or d\n")

menu = """\n---OUTPUT SELECT---
WAV file (wav)
PNG file (png)
CSV file (csv)
Awaiting input: """

while(1):
    output_mode = input(menu)
    if output_mode == "wav" or output_mode == "png" or output_mode == "csv":
        break
    print("\nInvalid input, please input wav, png or csv")
ser.close()

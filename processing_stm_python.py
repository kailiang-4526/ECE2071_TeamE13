import serial
import time
import wave
import numpy as np
import matplotlib.pyplot as plt
import csv

# Setup
port = "COM3"
baud = 115200
sample_rate = 9895


ser = serial.Serial(port, baud, timeout=5)



# Optimization: Read the entire block at once rather than byte-by-byte

def read_data_manual(samples):
    ser.write('M'.encode())
    print(f"Recording {samples/sample_rate} seconds...")
    time.sleep(1) # Give the port time to initialize
    audio = []
    ser.reset_input_buffer()
    print(samples)
    for i in range(samples):
        raw_data = ser.read(size=1)

        if raw_data:
            print(samples-i)
            audio.append(raw_data[0])

    data = np.array(audio)
    data = (data-data.min())/data.max()
    data = data*255
    data = data.astype(np.uint8)
    return data

def read_data_distance(distance):
    ser.write("D".encode())
    ser.write(distance.encode())
    print(f"Recording while within {distance}cm")
    time.sleep(1) # Give the port time to initialize
    audio = []
    raw_data=[]
    ser.reset_input_buffer()
    while raw_data != "\n":
        raw_data = ser.read(size=1)
        if raw_data:
            audio.append(raw_data[0])

    data = np.array(audio)
    data = (data-data.min())/data.max()
    data = data*255
    data = data.astype(np.uint8)
    return data

def export_wav(data:np.array, sample_rate):
    # Export to WAV
    with wave.open('output.wav', 'wb') as wf:
        wf.setnchannels(1)      # Mono
        wf.setsampwidth(1)      # 8-bit (1 byte per sample)
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())

    print("Done! Saved to output.wav")

def export_png(data:np.array):
    time = np.linspace(0, len(data)/sample_rate, len(data))

    plt.figure(10,4)
    plt.plot(time, data)

    plt.title("Amplitude vs Time Waveform of audio data")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('output.png')
    plt.show()
    print("Done! Saved as output.png")

def export_csv(data:np.array):
    filename = "output.csv"
    with open (filename, mode = 'w', newline = '') as file:
        writer = csv.writer(filename)
        writer.writerow(["Sample Rate", sample_rate])
        writer.writerow(["Sample Value"])
        for value in data:
            writer.writerow([value])
    print("Done! Saved as output.csv")



menu = """---RECORDING MODE SELECT---
Manual (m)
Distance Triggered (d)
Awaiting input: """

while(1):
    recording_mode = input(menu)
    if recording_mode == "d" or recording_mode == "m":
        break
    print("\nInvalid input, please input m or d\n")
if recording_mode == "d":
    while(1):
        distance = input("What distance should trigger recording (cm)? ")
        if distance.isnumeric():
            distance = int(distance)
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

if recording_mode == "m":
    duration = int(input("How many seconds of audio to record? "))
    total_samples = duration * sample_rate
    output = read_data_manual(total_samples)

else:
    pass

if output_mode == "wav":
    export_wav(output, sample_rate)
elif output_mode == "csv":
    export_csv(output)
else:
    export_png(output_mode)

ser.close()

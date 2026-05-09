import serial
import time
import wave
import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.signal import iirnotch, filtfilt

# Setup
port = "COM3"
baud = 921600
ser = serial.Serial(port, baud, timeout=10)

def apply_notch(data, freq=689.0, sample_rate=22050, Q=15):
    b, a = iirnotch(freq, Q, sample_rate)
    filtered = filtfilt(b, a, data.astype(np.float32))
    return np.clip(filtered, 0, 255).astype(np.uint8)

def diagnose_fft(samples=22050):  # 1 second
    ser.reset_input_buffer()
    ser.write('M\n'.encode())
    raw = ser.read(samples)
    data = np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128

    fft = np.abs(np.fft.rfft(data))
    freqs = np.fft.rfftfreq(len(data), d=1/22050)

    # Find peak
    peak_idx = np.argmax(fft[1:]) + 1  # skip DC
    print(f"Dominant noise frequency: {freqs[peak_idx]:.1f} Hz")

    plt.figure(figsize=(10, 4))
    plt.plot(freqs, fft)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title("FFT - find the noise spike")
    plt.xlim(0, 1000)  # zoom into low freq where hum lives
    plt.grid(True)
    plt.show()


def measure_sample_rate():
    print("Measuring sample rate for 1 second...")
    ser.reset_input_buffer()
    ser.write('M\n'.encode())
    time.sleep(0.1)           # let STM start streaming
    ser.reset_input_buffer()  # clear startup bytes
    time.sleep(1.0)           # measure for exactly 1 second
    count = ser.in_waiting
    ser.reset_input_buffer()
    print(f"Measured sample rate: {count} sps")
    return count

sample_rate = 22050 # 22050

# Optimization: Read the entire block at once rather than byte-by-byte

def read_data_manual(samples):

    print(f"Recording {samples/sample_rate} seconds...")

    ser.reset_input_buffer()
    ser.write('M\n'.encode())
    audio = []
    print(samples)
    raw = ser.read(samples)
    
    data = np.frombuffer(raw, dtype=np.uint8)
    
    print("Received:", len(data))

    data = (data - data.min()) / data.max()
    data = (data * 255).astype(np.uint8)

    return data

def read_data_distance(distance):
    ser.reset_input_buffer()
    if distance >= 10: send_string = 'D' + str(distance) + '\n'
    else: send_string = 'D' + '0' + str(distance) + '\n'
    print(send_string)
    ser.write(send_string.encode())

    print(f"Recording while within {distance}cm")
    audio = []
    
    time.sleep(0.1)
    while True:
        raw = ser.read(1)
        if not raw:
            break

        if raw == b'S':
            break

        audio.append(raw[0])
        
    print(len(audio))
    data = np.array(audio)
    data = (data-data.min())/data.max()
    data = data*255
    data = data.astype(np.uint8)
    return data

def export_wav(data:np.array, sample_rate):
    # Export to WAV
    with wave.open(r'C:\Users\Kai Liang\Desktop\ECE 2071\project\output.wav', 'wb') as wf:
        wf.setnchannels(1)      # Mono
        wf.setsampwidth(1)      # 8-bit (1 byte per sample)
        wf.setframerate(sample_rate)    
        wf.writeframes(data.tobytes())

    print("Done! Saved to output.wav")

def export_png(data:np.array):
    time = np.linspace(0, len(data)/sample_rate, len(data))

    plt.figure(figsize=(10, 4))
    plt.plot(time, data)

    plt.title("Amplitude vs Time Waveform of audio data")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(r'C:\Users\Kai Liang\Desktop\ECE 2071\project\output.png')
    plt.show()
    print("Done! Saved as output.png")

def export_csv(data:np.array):
    filename = r"C:\Users\Kai Liang\Desktop\ECE 2071\project\output.csv"
    with open (filename, mode = 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(["Sample Rate", sample_rate])
        writer.writerow(["Sample Value"])
        for value in data:
            writer.writerow([value])
    print("Done! Saved as output.csv")



print("========================================")
print("    STM32 AUDIO DATA CLI    ")
print("========================================\n")
menu = """---RECORDING MODE SELECT---
Manual (m)
Distance Triggered (d)
Awaiting input: """
distance = 0

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
elif recording_mode == "d":
    output = read_data_distance(distance)

else:
    pass

if output_mode == "wav":
    export_wav(output, sample_rate)
elif output_mode == "csv":
    export_csv(output)
else:
    export_png(output)

ser.close()

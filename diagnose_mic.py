import speech_recognition as sr
import pyaudio

print("PyAudio version:", pyaudio.__version__)
print("SpeechRecognition version:", sr.__version__)

try:
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    
    print(f"\nFound {numdevices} devices:")
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print(f"Input Device id {i} - {p.get_device_info_by_host_api_device_index(0, i).get('name')}")
            
    # p.terminate() # Don't terminate yet
    
    print("\nAttempting to list microphones via SpeechRecognition:")
    print(sr.Microphone.list_microphone_names())
    
    # Try recording from specific devices
    print("\nAttempting to record from specific devices...")
    for i in range(0, numdevices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            print(f"\nTesting Device {i}: {device_info.get('name')}")
            try:
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=44100,
                                input=True,
                                input_device_index=i,
                                frames_per_buffer=1024)
                print(f"  Stream opened successfully on Device {i}.")
                data = stream.read(1024, exception_on_overflow=False)
                print(f"  Read {len(data)} bytes of audio data.")
                stream.stop_stream()
                stream.close()
                print(f"  SUCCESS: Device {i} works!")
            except Exception as e:
                print(f"  FAILURE: Device {i} failed: {e}")
    
except Exception as e:
    print(f"Error checking microphone: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        if 'p' in locals():
            p.terminate()
    except:
        pass

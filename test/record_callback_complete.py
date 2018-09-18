"""
PyAudio Example: Make a wire between input and output (i.e., record a
few samples and play them back immediately).

This is the callback (non-blocking) version.
"""
import functools
import sys
import threading
import time

import pyaudio


WIDTH = 2
CHANNELS = 2
RATE = 44100

if sys.platform == 'darwin':
    CHANNELS = 1

p = pyaudio.PyAudio()

timer_dict_1 = {
    'stream_num': 1,
    'callback_count': 1,
    'complete_num': 10
}

for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))
# id=0 is built in mic
# id=3 is Soundflower (2ch)
input_device_id = 3

def func_willbreak():
    try:
        time.sleep(0.4)
        raise Exception('synthetic exception')
    except Exception as exc:
        print('I broke error=%s' % exc)

def callback(in_data, frame_count, time_info, status, timer_dict=None):
    print('stream_num=%s callback_count=%s' % (timer_dict['stream_num'], timer_dict['callback_count']))
    if timer_dict['callback_count'] < timer_dict['complete_num']:
        timer_dict['callback_count'] += 1
        return (in_data, pyaudio.paContinue)
    elif timer_dict['callback_count'] == timer_dict['complete_num']:
        timer_dict['callback_count'] += 1
        return (in_data, pyaudio.paComplete)
    else:
        # this should not be called
        timer_dict['callback_count'] += 1
        return (in_data, pyaudio.paComplete)

callback_1 = functools.partial(callback, timer_dict=timer_dict_1)
stream_1 = p.open(format=p.get_format_from_width(WIDTH),
                  channels=CHANNELS,
                  input_device_index=input_device_id,
                  rate=RATE,
                  input=True,
                  start=False,
                  stream_callback=callback_1)



def stream_runner(stream_1):
    stream_1.start_stream()

    thread_1 = threading.Thread(target=func_willbreak)
    thread_2 = threading.Thread(target=func_willbreak)
    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()

    while stream_1.is_active():
        time.sleep(0.1)
    stream_1.stop_stream()

    stream_1.close()
    p.terminate()

baby = threading.Thread(target=stream_runner, args=(stream_1,))

baby.start()

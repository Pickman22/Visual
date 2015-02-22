import pyaudio
from pylab import *
import numpy
import threading
from collections import deque

class Listener:

	RATE = 44100
	CHUNK_SIZE = 1024
	RECORD_TIME = 2.0 # seconds
	FORMAT = pyaudio.paFloat32
	CHANNELS = 1

	sound = deque([]) # Buffer to store audio strings.
	time_limit = 0.0
	llock = threading.Lock() # Lock to avoid race condition in sound buffer.
	recording_time = 0.0
	sampling_rate = 0.0
	done = False

	def __init__(self, rate = RATE, buffersize = CHUNK_SIZE, recording_time = RECORD_TIME, format = FORMAT, channels = CHANNELS):

		Listener.time_limit = recording_time	
		Listener.sampling_rate = rate

		self.rate = rate
		self.buffersize = buffersize
		self.p = pyaudio.PyAudio()

		self.stream = self.p.open(format = format,
			channels = channels,
			rate = self.rate,
			input = True,
			frames_per_buffer = buffersize,
			stream_callback = Listener.listen_callback,
			start = False)

	# Callback from the pyaudio library.
	@staticmethod
	def listen_callback(in_data, frame_count, time_info, status_flags):
		#print time_info
		with Listener.llock:
			Listener.sound.append(in_data)
		Listener.recording_time += float(len(in_data)) / Listener.sampling_rate
		if Listener.recording_time > Listener.time_limit and not Listener.time_limit < 0:
			Listener.done = True
			return None, pyaudio.paComplete
		else:
			return None, pyaudio.paContinue

	# Start streaming.
	def start(self):
		Listener.done = False
		self.stream.start_stream()

	# Close the stream. End.
	def stop(self):
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()
		#self.done = True

	# Blocks to wait for listener to finish recording.
	def wait(self):
		while not Listener.done:
			pass
		self.stop()

	# Get next value from the FIFO buffer.
	def popAudio(self, get_last = False):
		with Listener.llock:
			if Listener.sound:
				if get_last:
					audio = Listener.sound.pop()
				else:
					audio = Listener.sound.popleft()
			else:
				audio = ''
		return numpy.fromstring(audio, 'Float32')


	def clearBuffer(self):
		with Listener.llock:
			Listener.sound = deque([])


if __name__ == '__main__':
	l = Listener(recording_time = 2.0)
	l.start()
	l.wait()
	plot(l.popAudio())
	#print l.sound
	show()
	
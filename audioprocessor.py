from listener import Listener
import filter
import numpy
import threading
from collections import deque
from datetime import datetime
from time import sleep
from matplotlib import pyplot as plt

class AudioProcessor:

	TIME_LIMIT = 2.0

	LOW_CUTOFF = 7.0e3 # 7khz
	MID_CUTOFF = numpy.array([7.0e3, 14.0e3])
	HIGH_CUTOFF = 14.0e3

	def __init__(self, time_limit = TIME_LIMIT, low_cutoff = LOW_CUTOFF, mid_cutoff = MID_CUTOFF, high_cutoff = HIGH_CUTOFF):
		self.listener = Listener(recording_time = -1.0) # Execute forever. The stop condition is determined in this class.
		self.lfilter = filter.LowFilter(low_cutoff)
		self.mfilter = filter.MidFilter(mid_cutoff)
		self.hfilter = filter.HighFilter(high_cutoff)
		self.lstream = deque([])
		self.mstream = deque([])
		self.hstream = deque([])
		self.athread = threading.Thread(target = self.getAudio) 
		self.plock = threading.Lock()
		self.done = False
		self.timelimit = time_limit

	def start(self):
		print 'Started.'
		self.done = False
		self.athread.start()

	def pushRawAudio(self, audio):
		with self.plock:
			self.lstream.append(self.lfilter.filter(audio))
			self.mstream.append(self.mfilter.filter(audio))
			self.hstream.append(self.hfilter.filter(audio))

	def getAudio(self):
		self.setupListener()
		self.startingtime = datetime.now()
		while not self.done:
			if self.listener.sound:
				print 'Data available.'
				audio = self.listener.popAudio()
				self.pushRawAudio(audio)
			else:
				print 'No data available.'
			sleep(0.01) # Sleep 10 milliseconds.
			if self.elapsedSeconds() > self.timelimit:
				self.stop()

	def elapsedSeconds(self):
		return (datetime.now()-self.startingtime).total_seconds()

	def stop(self):
		self.listener.stop()
		self.done = True
		print 'Done.'

	def popFilteredAudio(self):
		with self.plock:
			laudio = self.lstream.popleft()
			maudio = self.mstream.popleft()
			haudio = self.hstream.popleft()
		return laudio, maudio, haudio

	def setupListener(self):
		self.listener.start()
		while not self.listener.sound: # Wait for listener.
			pass
		print 'Listener ready.'

	def isActive(self):
		return not self.done

	def plotFilterResponse(self):
		[lw, lh] = self.lfilter.response()
		[mw, mh] = self.mfilter.response()
		[hw, hh] = self.hfilter.response()
		plt.plot(lw, numpy.abs(lh))
		plt.plot(mw, numpy.abs(mh), 'r')
		plt.plot(hw, numpy.abs(hh), 'g')
		plt.legend(['Low pass', 'Band pass', 'High pass'])
		plt.title('Filter Response')
		plt.xlabel('Frequency [Hz]')
		plt.ylabel('Amplitude')
		plt.grid()
		plt.show()

if __name__ == '__main__':
	ap = AudioProcessor(time_limit = 1.0)
	ap.start()
	while ap.isActive():
		pass
	audio = ap.popFilteredAudio()
	plt.plot(audio[0])
	plt.plot(audio[1], 'r')
	plt.plot(audio[2], 'g')
	plt.show()
	#ap.plotFilterResponse()

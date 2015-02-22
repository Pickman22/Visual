from listener import Listener
from visualizer import Visualizer
import threading
import time
import matplotlib.pyplot as plt 
import matplotlib.animation as animation

import numpy

def create_plot(visualizer):
	fig = plt.figure()
	line, = plt.plot(range(1023), numpy.zeros([1023]))
	plt.xlim(-av.listener.rate/2.0, av.listener.rate/2.0)
	plt.ylim(0, 15)
	anim = animation.FuncAnimation(fig, visualizer.updatePlot, fargs = (line,), interval = 30)

class AudioVisualizer:

	def __init__(self, plot_fft = True):
		# Record forever. Rate: 44100. Buffer size: 1024.
		# Format: UINT8. Channels: 1. 

		self.lowTreshold = 1023 / 4.0 / 3.0
		self.midTreshold = 2.0 * 1023 / 4.0 / 3.0
		self.highThreshold = 1023 / 4.0

		self.listener = Listener(recording_time = -1.0)
		
		# Color update inside this thread.
		self.uthread = threading.Thread(target = self.update)

		# Screen size: 800x600. The event_callback notifies if the user
		# Closes the pygame window. The application should end.
		self.visualizer = Visualizer(event_callback = self.die_event)
		self.isactive = False
		self.fftaudio = numpy.array([])
		self.colors = (0, 0, 0)

	def start(self):
		self.listener.start() # Start reading microphone.
		self.visualizer.start() # Start the visualization window.
		self.isactive = True
		self.uthread.start() # Start the update thread.

	def die_event(self, die):
		if die: # The pygame window is closed by the user.
			self.stop() # Program should stop.
		else:
			pass

	def stop(self):
		self.listener.stop()
		self.isactive = False

	def update(self):
		while self.isactive:
			# Get the last audio data.
			audio = self.listener.popAudio(get_last = True) 
			#print audio
			self.listener.clearBuffer()
			if audio.any():
				self.mapAudioToColor(audio)
				self.updateColor()
			time.sleep(0.03)

	def updatePlot(self, frames, line):
		if self.fftaudio.any():
			freq = numpy.linspace(0, self.listener.rate/2.0, self.fftaudio.size)
			#line.set_xdata(freq)
			line.set_xdata(numpy.arange(self.fftaudio.size))
			line.set_ydata(self.fftaudio)


	# Map the audio data to a visualization. Maybe instead
	# of the filters, use an FFT to map the maginutde of the maximum
	# value within low, mid and high frequency to RGB colors.
	def mapAudioToColor(self, audio):
		#self.fftaudio = numpy.abs(numpy.fft.fftshift(numpy.fft.fft(audio))) # Fourier transform data.
		#self.fftaudio = numpy.abs(numpy.fft.fft(audio))[0:audio.size/2]

		self.fftaudio = numpy.abs(numpy.fft.fft(audio))[30:300] # Drop useless data.

		r = numpy.max(self.fftaudio[0:80])
		g = numpy.max(self.fftaudio[80:170])
		b = numpy.max(self.fftaudio[170:])

		#b = numpy.max(self.fftaudio[0:self.lowTreshold])
		#r = numpy.max(self.fftaudio[self.lowTreshold:self.midTreshold])
		#g = numpy.max(self.fftaudio[self.midTreshold:])

		#b = 250 * b / 500.0
		#r = 250 * r / 50.0
		#g = 250 * g / 50.0

		r = (b / 30.0) * 255
		g = (g / 30.0) * 255
		b = (b / 30.0) * 255


		if r > 255: r = 255
		if g > 255: g = 255
		if b > 255: b = 255

		self.colors = (r, g, b)

	# Just update the color of the screen to simulate visualization.
	def updateColor(self):
		self.visualizer.setColor(self.colors)


if __name__ == '__main__':
	av = AudioVisualizer()
	fig = plt.figure()
	line, = plt.plot(range(1023), numpy.zeros([1023]))
	#plt.xlim(0, av.listener.rate/2.0)
	plt.xlim(30, 300)
	plt.ylim(0, 50)
	anim = animation.FuncAnimation(fig, av.updatePlot, fargs = (line,), interval = 30)
	plt.grid()
	plt.xlabel('Frequency [Hz]')
	plt.ylabel('Maginutde')
	#create_plot(av)
	av.start()
	plt.show()
	print 'Start.'
	while av.isactive:
		pass
	print 'Done.'

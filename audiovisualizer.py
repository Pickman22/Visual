from listener import Listener
from visualizer import Visualizer
import threading
import time

class AudioVisualizer:

	def __init__(self):

		# Record forever. Rate: 44100. Buffer size: 1024.
		# Format: UINT8. Channels: 1. 
		self.listener = Listener(recording_time = -1.0)
		self.uthread = threading.Thread(target = self.update)
		# Screen size: 800x600
		self.visualizer = Visualizer(event_callback = self.die_event)
		self.isActive = False

	def start(self):
		self.listener.start()
		self.visualizer.start()
		self.isActive = True
		self.uthread.start()

	def die_event(self, die):
		if die:
			self.stop()

	def stop(self):
		self.listener.stop()
		self.isActive = False

	def update(self):
		while self.isActive:
			audio = self.listener.popAudio(get_last = True)
			#print audio
			self.listener.clearBuffer()
			self.mapAudioToColor()
			time.sleep(0.03)

	def mapAudioToColor(self):
		pass

	def updateColor(self):
		pass


if __name__ == '__main__':
	av = AudioVisualizer()
	av.start()
	print 'Start.'
	while av.isActive:
		pass
	print 'Done.'

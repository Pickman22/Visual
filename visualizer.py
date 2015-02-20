import pygame, sys, time
import threading

class Visualizer:

	BLACK  = 0, 0, 0
	GREEN = 0, 255, 0
	RED = 255, 0, 0
	BLUE = 0, 0, 255
	WHITE = 255, 255, 255

	WIDTH = 800
	HEIGHT = 600

	def __init__(self, size = (WIDTH, HEIGHT), **kwargs):
		pygame.init()
		self.size = size
		if kwargs.has_key('event_callback'):
			self.call = kwargs['event_callback']
		else:
			self.call = None
		

	def start(self):
		self.screen = pygame.display.set_mode(self.size)
		self.screen.fill(self.BLACK)
		pygame.display.flip()
		self.isActive = True
		self.qthread = threading.Thread(target = self.watchQuit)
		self.qthread.start()

	def watchQuit(self):
		while self.isActive:
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					if self.call is not None:
						self.call(True) # Die.
					self.stop()
			time.sleep(0.01)

	def setColor(self, color):
		try:
			self.screen.fill(color)
		except pygame.error:
			print 'Visualizer is not active.'
			self.stop()
			return
		pygame.display.flip()

	def stop(self):
		self.isActive = False
		pygame.quit()
		sys.exit()

if __name__ == '__main__':
	v = Visualizer()
	v.start()
	for i in range(250):
		v.setColor((0, i, i))
		time.sleep(0.05)
	v.stop()	
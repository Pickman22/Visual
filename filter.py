import numpy
from scipy.signal import lfilter, filtfilt, freqz, butter
import wave

class Filter(object):
	RATE = 44100.0
	NYQ_RATE = RATE/2.0
	FILT_ORDER = 2
	
	def __init__(self, cutoff, rate, filt_order, filt_type):
		self.cutoff_frequency = cutoff
		self.rate = rate
		self.nyquist_rate = rate / 2.0
		self.cutoff_frequency_norm = self.cutoff_frequency / self.nyquist_rate
		self.filt_order = filt_order
		self.filter_type = filt_type

	def filter_design(self):
		raise NotImplementedError

	def filter(self, signal):
		raise NotImplementedError

	def response(self):
		w, h = freqz(self.b, self.a)
		return self.nyquist_rate * w / numpy.pi, numpy.abs(h)

class LowFilter(Filter):
	def __init__(self, cutoff_freq, rate = Filter.RATE, filt_order = Filter.FILT_ORDER):
		Filter.__init__(self, cutoff_freq, rate, filt_order, 'lowpass')
		self.filter_design()

	def filter_design(self):
		self.b, self.a = butter(self.filt_order, self.cutoff_frequency_norm, btype = 'lowpass')

	def filter(self, signal):
		return filtfilt(self.b, self.a, signal)

class MidFilter(Filter):
	def __init__(self, cutoff_freq, rate = Filter.RATE, filt_order = Filter.FILT_ORDER):
		Filter.__init__(self, cutoff_freq, rate, filt_order, 'bandpass')
		self.filter_design()

	def filter_design(self):
		self.b, self.a = butter(self.filt_order, self.cutoff_frequency_norm, btype = 'bandpass')

	def filter(self, signal):
		return filtfilt(self.b, self.a, signal)

class HighFilter(Filter):
	HIGH_SIDE_CUTOFF = 20.0e3

	def __init__(self, cutoff_freq, rate = Filter.RATE, filt_order = Filter.FILT_ORDER):
		if cutoff_freq >= self.HIGH_SIDE_CUTOFF:
			raise ValueError('Cutoff frequency larger than high side cutoff frequency: %s' % self.HIGH_SIDE_CUTOFF)
		cutoff = numpy.array([cutoff_freq, self.HIGH_SIDE_CUTOFF])
		Filter.__init__(self, cutoff, rate, filt_order, 'bandpass')
		self.filter_design()

	def filter_design(self):
		self.b, self.a = butter(self.filt_order, self.cutoff_frequency_norm, btype = 'bandpass')

	def filter(self, signal):
		return filtfilt(self.b, self.a, signal)

if __name__ == '__main__':
	import pyaudio
	chunk = 1024
	bigben = wave.open('chime_big_ben.wav')
	p = pyaudio.PyAudio()
	channel_map = (0, 1)
	lf = LowFilter(20.0e3)

	stream = p.open(format = p.get_format_from_width(bigben.getsampwidth()),
		channels = bigben.getnchannels(),
		rate = bigben.getframerate(),
		output = True)

	data = bigben.readframes(chunk)
	while data != '':
		audio_data = numpy.fromstring(data, dtype = numpy.uint8)
		audio_data = lf.filter(audio_data).astype(numpy.uint8).tostring()
		stream.write(audio_data)
		data = bigben.readframes(chunk)
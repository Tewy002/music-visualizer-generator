import sys, numpy, pygame

from pydub import AudioSegment
from scipy.fftpack import dct

BARS = 50 # number of bars
HEIGHT = 100 # height of bars
WIDTH = 12 # width of bars
FPS = 60

file_name = sys.argv[1]
status = "stopped"
clock = pygame.time.Clock()

#screen
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode([BARS * WIDTH, 50 + HEIGHT]) 
pygame.display.set_caption('Audio Visualizer')

#music player
pygame.mixer.music.load(file_name)
pygame.mixer.music.play()
pygame.mixer.music.set_endevent()
status = "playing"

#mp3 audio data
audio = AudioSegment.from_file(file_name)
framerate = audio.frame_rate
samples = numpy.array(audio.get_array_of_samples())
wave_data = samples.reshape((-1, 2)).T
frames = wave_data.shape[1]

#mp3 metadata

n = frames
#visualizer
    #make it smoother
h2 = numpy.zeros(BARS)
SMOOTHING = 0.18

def visualizer(n):
    global h2
    n = int(n)
    CHUNK = 1024
    start = max(0, frames - n)
    end = start + CHUNK
    signal = wave_data[0][start:end]
    window = numpy.hanning(CHUNK)
    signal = signal * window
    fft_data = numpy.abs(numpy.fft.rfft(signal))
    if len(signal) < CHUNK:
        signal = numpy.pad(signal, (0, CHUNK - len(signal)))

    h = []
    for i in range(BARS):
        start_idx = int((i / BARS) ** 2 * len(fft_data))
        end_idx = int(((i + 1) / BARS) ** 2 * len(fft_data))

        if end_idx <= start_idx:
            end_idx = start_idx + 1
        value = numpy.mean(fft_data[start_idx:end_idx])

    

#scaling
        value = min(HEIGHT, int((value ** 0.3) * HEIGHT / 130))
        h.append(value)
#smooth animation
    h2[:] = h2 + (h - h2) * SMOOTHING
    draw_bars(h2)

def render(status):
    global n
    if status == "stopped":
        n = frames
        return
    else:
        music_pos_ms = max(0, pygame.mixer.music.get_pos())
        music_pos_frames = int((music_pos_ms / 1000) * framerate)
        n = frames - music_pos_frames
        if n > 0:
            visualizer(n)

def draw_bars(h):
    bars = []
    for i in h:
        bars.append([len(bars) * WIDTH,50 + HEIGHT-i,WIDTH - 1,i])
    for i in bars:
        pygame.draw.rect(screen,[255,255,255],i,0)

#audio controller

#image display

#text display

#main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill((0,0,0))
    clock.tick(FPS)
    render(status)
    pygame.display.update()

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
screen = pygame.display.set_mode([BARS * WIDTH, + HEIGHT]) 
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
    #make the visualizer
    #audio frequency mapping
    #make it look good lmao

temp = []

def visualizer(n):
    n = int(n)
    h = abs(dct(wave_data[0][frames - n:frames - n + BARS *2]))
    h = [min(HEIGHT,int(i **(1 / 2.5) * HEIGHT / 100)) for i in h]
    draw_bars(h)

def render(status):
    global n
    if status == "stopped":
        n = frames
        return
    else:
        n -= framerate/FPS
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

import sys, numpy, pygame

from pydub import AudioSegment

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
screen = pygame.display.set_mode([BARS * WIDTH, HEIGHT]) 
pygame.display.set_caption('Audio Visualizer')

#music player
pygame.mixer.music.load(file_name)
pygame.mixer.music.play()
pygame.mixer.music.set_endevent()
status = "playing"

#mp3 audio data

#mp3 metadata

#visualizer

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

    pygame.display.update()

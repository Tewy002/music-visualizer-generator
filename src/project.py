import sys, numpy, pygame

from tinytag import TinyTag
from pydub import AudioSegment

BARS = 90 # number of bars
HEIGHT = 400 # height of bars
WIDTH = 20 # width of bars
FPS = 60

file_name = sys.argv[1]
status = "stopped"
clock = pygame.time.Clock()

#screen
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
pygame.display.set_caption('Audio Visualizer')

#music player
pygame.mixer.music.load(file_name)
pygame.mixer.music.play()
pygame.mixer.music.set_endevent()

#volume control
def set_volume(level):
    pygame.mixer.music.set_volume(level)
def change_volume(dv):
    current_volume = pygame.mixer.music.get_volume()
    new_volume = max(0, min(1, current_volume + dv))
    pygame.mixer.music.set_volume(new_volume)

status = "playing"
set_volume(1)

#mp3 audio data
audio = AudioSegment.from_file(file_name)
framerate = audio.frame_rate
samples = numpy.array(audio.get_array_of_samples())
wave_data = samples.reshape((-1, 2)).T
frames = wave_data.shape[1]

n = frames
#visualizer
    #make it smoother
h2 = numpy.zeros(BARS)
SMOOTHING = 0.09

def visualizer(n):
    global h2
    n = int(n)
    if n < 0:
        return
    CHUNK = 2048
    start = max(0, frames - n)
    end = min(start + CHUNK, frames)
    if start >= frames:
        return
    signal = wave_data[0][start:end]
    if len(signal) < CHUNK:
        signal = numpy.pad(signal, (0, CHUNK - len(signal)))
    fft_data = numpy.abs(numpy.fft.rfft(signal))

    h = []
    for i in range(BARS):
        start_idx = int((i / BARS) ** 2 * len(fft_data))
        end_idx = int(((i + 1) / BARS) ** 2 * len(fft_data))

        if end_idx <= start_idx:
            end_idx = start_idx + 1
        value = numpy.mean(fft_data[start_idx:end_idx])

#scaling
        value = min(HEIGHT, int((value ** 0.3) * HEIGHT / 100))
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
        music_pos_ms = pygame.mixer.music.get_pos()
        if music_pos_ms < 0:
            return
        music_pos_frames = int((music_pos_ms / 1000) * framerate)
        n = frames - music_pos_frames
        if n > 0:
            visualizer(n)

def draw_bars(h):
    bars = []
    for i in h:
        bars.append([56 +len(bars) * WIDTH, 620 + HEIGHT-i,WIDTH - 4,i])
    for i in bars:
        pygame.draw.rect(screen,[255,255,255],i,0)

#image display - load once during initialization
bg = sys.argv[2]
ab = sys.argv[3]

background_img = pygame.image.load(bg)
background_img = pygame.transform.scale(background_img, (1920, 1080))
album_img = pygame.image.load(ab)
album_img = pygame.transform.scale(album_img, (700, 700))

def background(x, y):
    screen.blit(background_img, (x, y))
def album_art(x, y):
    screen.blit(album_img, (x, y))

#mp3 metadata
tag = TinyTag.get(file_name)
artist = tag.artist if tag.artist else ""
title = tag.title if tag.title else ""
album = tag.album if tag.album else ""
genre = tag.genre if tag.genre else ""
year = str(tag.year) if tag.year else ""
#text display - create fonts once during initialization
#title
#artist
#album
#genre
#year
#timecode (changes)
font_timecode = pygame.font.SysFont('Yu Gothic', 30)


def draw_text(text, size, x, y):
    font = pygame.font.SysFont('Yu Gothic', size)
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (x, y))
def draw_timecode(size, x, y):
    font_timecode = pygame.font.SysFont('Yu Gothic', size)
    if status == "stopped":
        timecode = "0:00"
    else:
        music_pos_ms = pygame.mixer.music.get_pos()
        if music_pos_ms < 0:
            timecode = "0:00"
        else:
            total_seconds = music_pos_ms // 1000
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            timecode = f"{minutes}:{seconds:02d}"
    text_surface = font_timecode.render(timecode, True, (255, 255, 255))
    screen.blit(text_surface, (x, y))

def main():
    global status
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            #keyboard controls
            elif event.type == pygame.USEREVENT:
                status = "stopped"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_volume(0.1)
                elif event.key == pygame.K_DOWN:
                    change_volume(-0.1)
                elif event.key == pygame.K_SPACE:
                    if status == "playing":
                        pygame.mixer.music.pause()
                        status = "paused"
                    elif status in ("paused", "stopped"):
                        pygame.mixer.music.unpause()
                        status = "playing"
                elif event.key == pygame.K_RETURN:
                    if status in ("playing", "paused"):
                        pygame.mixer.music.stop()
                        status = "stopped"
                    else:
                        pygame.mixer.music.play()
                        status = "playing"
                elif event.key == pygame.K_ESCAPE:
                    sys.exit()

        
        if n <= 0:
            status = "stopped"
        screen.fill((0,0,0))
        clock.tick(FPS)
        background(0, 0)
        album_art(1130, 90)
        render(status)
        draw_text(title, 80, 90, 90)
        draw_text(artist, 70, 90, 200)
        draw_text(album, 50, 90, 300)
        draw_text(genre, 50, 90, 380)
        draw_text(year, 50, 90, 460)
        draw_timecode(50, 90, 540)
        pygame.display.update()

if __name__ == "__main__":
    main()

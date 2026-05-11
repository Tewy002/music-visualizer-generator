import sys, numpy, pygame, time

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

#image display - load once during initialization
background_img = None
album_img = None

if sys.argv[2] != 'none':
    bg = sys.argv[2]
    background_img = pygame.image.load(bg)
    background_img = pygame.transform.scale(background_img, (1920, 1080))

if sys.argv[3] != 'none':
    ab = sys.argv[3]
    album_img = pygame.image.load(ab)
    album_img = pygame.transform.scale(album_img, (700, 700))

def background(x, y):
    if background_img:
        screen.blit(background_img, (x, y))
def album_art(x, y):
    if album_img:
        screen.blit(album_img, (x, y))
#music player
def load_music(file_name):
    pygame.mixer.music.load(file_name)

#volume control
def set_volume(level):
    pygame.mixer.music.set_volume(level)
def change_volume(dv):
    current_volume = pygame.mixer.music.get_volume()
    new_volume = max(0, min(1, current_volume + dv))
    pygame.mixer.music.set_volume(new_volume)

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

#cache stuff https://aaronnotes.com/2023/04/caching-in-python/
cache = {}
cache_size = 100

def visualizer(n):
    global h2, cache
    n = int(n)
    if n < 0:
        return
    cache_key = n // 100
    if cache_key in cache:
        fft_data = cache[cache_key]
    else:
        CHUNK = 2048
        start = max(0, frames - n)
        end = min(start + CHUNK, frames)
        if start >= frames:
            return
        signal = wave_data[0][start:end]
        if len(signal) < CHUNK:
            signal = numpy.pad(signal, (0, CHUNK - len(signal)))
        fft_data = numpy.abs(numpy.fft.rfft(signal))

        if len(cache) >= cache_size:
            oldest_key = min(cache.keys())
            del cache[oldest_key]
        cache[cache_key] = fft_data
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
bar_pos = []
for i in range(BARS):
    bar_pos.append((56 + i * WIDTH, 620 + HEIGHT, WIDTH - 4))

def draw_bars(h):
    for i in range(BARS):
        x, base_y, width = bar_pos[i]
        height = int(h[i])
        y = base_y - height
        pygame.draw.rect(screen, [255, 255, 255], (x, y, width, height), 0)

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

size = [80, 70, 50]
font_title = pygame.font.SysFont('Yu Gothic', size[0])
font_artist = pygame.font.SysFont('Yu Gothic', size[1])
font = pygame.font.SysFont('Yu Gothic', size[2])
font_timecode = pygame.font.SysFont('Yu Gothic', size[2])

text_surface = {}
timecode_surface = None
last_timecode = 0

def draw_text(text, font, x, y):
    global text_surface
    key = (text, font)
    if key not in text_surface:
        text_surface[key] = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface[key], (x, y))

def draw_timecode(x, y):
    global timecode_surface
    global last_timecode
    if status == "stopped":
        timecode2 = last_timecode
    else:
        music_pos_ms = pygame.mixer.music.get_pos()
        if music_pos_ms < 0:
            timecode2 = last_timecode
        else:
            timecode2 = music_pos_ms
            last_timecode = music_pos_ms
    total_seconds = timecode2 // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    timecode = f"{minutes}:{seconds:02d}"
    text_surface = font_timecode.render(timecode, True, (255, 255, 255))
    screen.blit(text_surface, (x, y))

def draw_metadata():
    y = 90
    line_spacing = 60
    if title:
        draw_text(title, font_title, 90, y)
        y += 30 + line_spacing
    if artist:
        draw_text(artist, font_artist, 90, y)
        y += 20 + line_spacing
    if album:
        draw_text(album, font, 90, y)
        y += line_spacing
    if genre:
        draw_text(genre, font, 90, y)
        y += line_spacing
    if year:
        draw_text(year, font, 90, y)
        y += line_spacing
    return y


def main():
    global status, last_timecode
    running = True
    status = "stopped"
    last_timecode = 0
    load_music(file_name)
    prev_time = time.perf_counter()
    dt = 0
    target_time = 1 / FPS
    accumulated_time = 0
    while running:
        now = time.perf_counter()
        dt = now - prev_time
        prev_time = now
        dt = min(dt, 1 / 30)
        accumulated_time += dt

        if accumulated_time >= target_time:
            accumulated_time -= target_time
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
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
                            if status == "stopped":
                                last_timecode = 0
                            pygame.mixer.music.unpause()
                            status = "playing"
                    elif event.key == pygame.K_RETURN:
                        if status in ("playing", "paused"):
                            pygame.mixer.music.stop()
                            status = "stopped"
                        else:
                            last_timecode = 0
                            pygame.mixer.music.play()
                            status = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            if n <= 0:
                status = "stopped"
            screen.fill((0,0,0))
            background(0, 0)
            album_art(1130, 90)
            render(status)
            spacing = draw_metadata()
            draw_timecode(90, spacing)
            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

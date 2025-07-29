import sdl2
import sdl2.ext
import ctypes
import os
from PIL import Image

class Surface:
    def __init__(self, texture, width, height):
        self.texture = texture
        self.width = width
        self.height = height

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def to_sdl_rect(self):
        return sdl2.SDL_Rect(self.x, self.y, self.w, self.h)

    def colliderect(self, other):
        return (self.x < other.x + other.w and
                self.x + self.w > other.x and
                self.y < other.y + other.h and
                self.y + self.h > other.y)

class Clock:
    def __init__(self):
        self.last = sdl2.SDL_GetTicks()

    def tick(self, fps):
        now = sdl2.SDL_GetTicks()
        delay = int(1000/fps) - (now - self.last)
        if delay > 0:
            sdl2.SDL_Delay(delay)
        self.last = sdl2.SDL_GetTicks()

class EventType:
    QUIT = "QUIT"
    KEYDOWN = "KEYDOWN"
    KEYUP = "KEYUP"
    MOUSEBUTTONDOWN = "MOUSEBUTTONDOWN"
    MOUSEBUTTONUP = "MOUSEBUTTONUP"
    MOUSEMOTION = "MOUSEMOTION"

class Event:
    def __init__(self, type_, **attrs):
        self.type = type_
        for k, v in attrs.items():
            setattr(self, k, v)

class Display:
    def __init__(self):
        self.window = None
        self.renderer = None
        self.width = 0
        self.height = 0
        self.running = False
        self.clear_color = sdl2.ext.Color(0, 0, 0)

    def set_mode(self, size):
        w, h = size
        self.width = w
        self.height = h
        if self.window:
            sdl2.SDL_DestroyRenderer(self.renderer)
            sdl2.SDL_DestroyWindow(self.window)
        self.window = sdl2.SDL_CreateWindow(b"Viper Engine", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, w, h, sdl2.SDL_WINDOW_SHOWN)
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
        sdl2.SDL_SetRenderDrawBlendMode(self.renderer, sdl2.SDL_BLENDMODE_BLEND)
        self.running = True
        _set_window_icon(self)
        return self

    def set_caption(self, title):
        if self.window:
            sdl2.SDL_SetWindowTitle(self.window, title.encode("utf-8"))

    def fill(self, color):
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl2.SDL_RenderClear(self.renderer)

    def update(self):
        sdl2.SDL_RenderPresent(self.renderer)

    def flash(self, surface, dest):
        if not isinstance(dest, Rect):
            dest = Rect(dest[0], dest[1], surface.get_width(), surface.get_height())
        sdl_rect = dest.to_sdl_rect()
        sdl2.SDL_RenderCopy(self.renderer, surface.texture, None, sdl_rect)

    def draw_rect(self, color, rect, width=0):
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl_rect = rect.to_sdl_rect()
        if width == 0:
            sdl2.SDL_RenderFillRect(self.renderer, sdl_rect)
        else:
            for i in range(width):
                rct = sdl2.SDL_Rect(rect.x+i, rect.y+i, rect.w-2*i, rect.h-2*i)
                sdl2.SDL_RenderDrawRect(self.renderer, rct)

    def draw_line(self, color, start_pos, end_pos):
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl2.SDL_RenderDrawLine(self.renderer, start_pos[0], start_pos[1], end_pos[0], end_pos[1])

    def draw_point(self, color, pos):
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl2.SDL_RenderDrawPoint(self.renderer, pos[0], pos[1])

def _set_window_icon(display):
    path = os.path.join(os.path.dirname(__file__), "Viper.png")
    image = Image.open(path)
    image = image.convert("RGBA")
    w, h = image.size
    data = image.tobytes()
    surf = sdl2.SDL_CreateRGBSurfaceFrom(data, w, h, 32, w * 4, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000)
    sdl2.SDL_SetWindowIcon(display.window, surf)
    sdl2.SDL_FreeSurface(surf)

def init():
    return sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_AUDIO) == 0

def quit():
    sdl2.SDL_Quit()

def load_image(path, display):
    surface = sdl2.ext.load_image(path)
    texture = sdl2.SDL_CreateTextureFromSurface(display.renderer, surface)
    width = surface.contents.w
    height = surface.contents.h
    sdl2.SDL_FreeSurface(surface)
    return Surface(texture, width, height)

def event_get():
    events = []
    event = sdl2.SDL_Event()
    while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
        etype = event.type
        if etype == sdl2.SDL_QUIT:
            events.append(Event(EventType.QUIT))
        elif etype == sdl2.SDL_KEYDOWN:
            events.append(Event(EventType.KEYDOWN, key=event.key.keysym.sym))
        elif etype == sdl2.SDL_KEYUP:
            events.append(Event(EventType.KEYUP, key=event.key.keysym.sym))
        elif etype == sdl2.SDL_MOUSEBUTTONDOWN:
            events.append(Event(EventType.MOUSEBUTTONDOWN, pos=(event.button.x, event.button.y), button=event.button.button))
        elif etype == sdl2.SDL_MOUSEBUTTONUP:
            events.append(Event(EventType.MOUSEBUTTONUP, pos=(event.button.x, event.button.y), button=event.button.button))
        elif etype == sdl2.SDL_MOUSEMOTION:
            events.append(Event(EventType.MOUSEMOTION, pos=(event.motion.x, event.motion.y), rel=(event.motion.xrel, event.motion.yrel)))
    return events

def key_get_pressed():
    sdl2.SDL_PumpEvents()
    numkeys = ctypes.c_int(0)
    keys = sdl2.SDL_GetKeyboardState(ctypes.byref(numkeys))
    pressed = set()
    for i in range(numkeys.value):
        if keys[i]:
            pressed.add(i)
    return pressed

_display = None

def display_set_mode(size):
    global _display
    if _display is None:
        _display = Display()
    return _display.set_mode(size)

def display_set_caption(title):
    if _display is not None:
        _display.set_caption(title)

def display_flip():
    if _display is not None:
        _display.update()

def get_display():
    return _display

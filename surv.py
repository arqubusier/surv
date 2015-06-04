import sys
import os
import sdl2.ext
import sdl2

root_dir = os.path.dirname(os.path.abspath(__file__))
resources = sdl2.ext.Resources(os.path.join(root_dir, "resources"))

#
# CHANGE THESE!!!
#

BLACK = sdl2.ext.Color(0, 0, 0)
WHITE = sdl2.ext.Color(255, 255, 255)
PINK = sdl2.ext.Color(255, 255, 255)
GEEN = sdl2.ext.Color(255, 255, 255)
ORANGE = sdl2.ext.Color(255, 255, 255)

SCALE_X = 1/2400 * 1/4
SCALE_Y = SCALE_X

class Vector2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Vector3D(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

Pos2D = Vector2D
Pos3D = Vector3D
Vel2D = Vector2D
Vel3D = Vector3D
Dim2D = Vector2D
Dim3D = Vector3D


class Rectangle(object):
    def __init__(self, x, y, z, len_x, len_y, color):
        self.pos = Pos3D(x, y, z)
        self.dim = Dim2D(len_x, len_y)
        self.color = color
    
    def draw(self, renderer, room):
        """Draws the rect, scaling the width and height and offsetting the x and y coordinates according to the
        the z-coordinate. These operations are both linear functions of z"""
        #The ratio of the opposing wall to the front facing wall
        ratio = 0.25
        gradient_x = (ratio - 1)*self.dim.x/room.dim.z
        gradient_y = (ratio - 1)*self.dim.y/room.dim.z

        dim_x = gradient_x*self.pos.z + self.dim.x
        dim_y = gradient_y*self.pos.z + self.dim.y

        gradient_x = (1 - ratio) * room.dim.x / 2 / room.dim.z
        gradient_y = (1 - ratio) * room.dim.y / 2 / room.dim.z
        offset_x = gradient_x*self.pos.z
        offset_y = gradient_y*self.pos.z

        x = self.pos.x + offset_x
        y = self.pos.y + offset_y

        renderer.draw_rect((round(x), round(y), round(dim_x), round(dim_y)), self.color)

class Paddle(object):
    LENGTH_X = 80
    LENGTH_y = 60

    def __init__(self, x, y, z, vel_x, vel_y):
        self.pos = Pos3D(x, y, z)
        self.vel = Vel2D(vel_x, vel_y)
        self.dim = Dim2D(LENGTH_X, LENGTH_y)

    def handle_collision(self, room):
        pass

    def draw(self, renderer):
        pass

class Ball(object):
    LENGTH_X = 15
    LENGTH_y = 15
    LENGTH_Z = 15

    def __init__(self, x, y, z, vel_x, vel_y, vel_z):
        self.pos = Pos3D(x, y, z)
        self.vel = Vel3D(vel_x, vel_y, vel_z)
        self.dim = Dim3D(LENGTH_X, LENGTH_Y, LENGTH_Z)

    def handle_collision(paddle_1, paddle_2, room):
        pass

    def draw(self, renderer):
        pass

class Room(object):
    LENGTH_X = 800
    LENGTH_Y = 600
    LENGTH_Z = 2400

    def __init__(self):
        self.dim = Dim3D(Room.LENGTH_X, Room.LENGTH_Y, Room.LENGTH_Z)
        rects_spacing = Room.LENGTH_Z//8
        self.rects = [Rectangle(0, 0, z, Room.LENGTH_X, Room.LENGTH_Y, WHITE)
                for z in range(0, Room.LENGTH_Z + rects_spacing , rects_spacing)]

    def draw(self, renderer):
        #Rectangle(0, 0, 0, Room.LENGTH_X, Room.LENGTH_Y, WHITE).draw(renderer, self)
        for rect in self.rects:
            rect.draw(renderer, self)

def main():
    sdl2.ext.init()
    window = sdl2.ext.Window("SURV!", size=(800, 600))
    window.show()
    renderer = sdl2.ext.Renderer(window)

    room = Room()

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_UP:
                    pass
                    #move player up
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    pass
                    #move player down
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    #stop moving
                    pass
        renderer.clear(BLACK)
        room.draw(renderer)
        sdl2.SDL_Delay(10)
        renderer.present()

    return 0

    sdl2.ext.quit()

if __name__ == "__main__":
    sys.exit(main())

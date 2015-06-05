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
GREEN = sdl2.ext.Color(0, 255, 0)
ORANGE = sdl2.ext.Color(255, 0, 0)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
COURT_LENGTH = 2400

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

SCENE_DEFAULT = Dim3D(SCREEN_WIDTH, SCREEN_HEIGHT, COURT_LENGTH)

class Figure(object):
    #The ratio of the opposing wall to the front facing wall
    RATIO = 0.25
    scene = SCENE_DEFAULT
    def __init__(self, x, y, z, len_x, len_y, color):
        self.pos = Pos3D(x, y, z)
        self.dim = Dim2D(len_x, len_y)
        self.color = color
        self.redraw = True

    def scale_dim(self):
        gradient_x = (Figure.RATIO - 1)*self.dim.x/Figure.scene.z
        gradient_y = (Figure.RATIO - 1)*self.dim.y/Figure.scene.z

        dim_x = gradient_x*self.pos.z + self.dim.x
        dim_y = gradient_y*self.pos.z + self.dim.y
        
        return (dim_x, dim_y)

    def scale_pos(self):
        offs_slope_x = (1 - Figure.RATIO) * Figure.scene.x / 2 / Figure.scene.z
        offs_slope_y = (1 - Figure.RATIO) * Figure.scene.y / 2 / Figure.scene.z
        offset_x = offs_slope_x*self.pos.z
        offset_y = offs_slope_y*self.pos.z

        pos_slope_x = (Figure.RATIO - 1)*self.pos.x/Figure.scene.z
        pos_slope_y = (Figure.RATIO - 1)*self.pos.y/Figure.scene.z


        x = pos_slope_x*self.pos.z + self.pos.x
        y = pos_slope_y*self.pos.z + self.pos.y
        
        return (x + offset_x, y + offset_y)

    def move(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self.redraw = True

    def should_redraw(self):
        old_val = self.redraw
        redraw = False
        return old_val

class Rectangle(Figure):
    def __init__(self, x, y, z, len_x, len_y, color):
        super().__init__(x, y, z, len_x, len_y, color)

    def draw(self, renderer):
        """Draws the rect, scaling the width and height and offsetting the x and y coordinates according to the
        the z-coordinate. These operations are both linear functions of z"""
        if not super().should_redraw():
            return

        dim_x, dim_y = super().scale_dim()
        x, y = super().scale_pos()
        
        renderer.draw_rect((round(x), round(y), round(dim_x), round(dim_y)), self.color)

class Paddle(object):
    LENGTH_X = 80
    LENGTH_Y = 60

    def __init__(self, x, y, z, vel_x, vel_y, color):
        self.pos = Pos3D(x, y, z)
        self.vel = Vel2D(vel_x, vel_y)
        self.rect = Rectangle(x, y, z, Paddle.LENGTH_X, Paddle.LENGTH_Y, color)

    def handle_collision(self, room):
        pass

    def draw(self, renderer):
        self.rect.draw(renderer)

class Ball(object):
    LENGTH_X = 15
    LENGTH_Y = 15
    LENGTH_Z = 15

    def __init__(self, x, y, z, vel_x, vel_y, vel_z):
        self.pos = Pos3D(x, y, z)
        self.vel = Vel3D(vel_x, vel_y, vel_z)

    def handle_collision(paddle_1, paddle_2, room):
        pass

    def draw(self, renderer):
        #Draw proper disc!!!
        Rectangle(self.pos.x, self.pos.y, self.pos.z, Ball.LENGTH_X, Ball.LENGTH_Y, PINK).draw(renderer)

class Room(object):
    dim = SCENE_DEFAULT
    def __init__(self):
        rects_spacing = Room.dim.z//8
        self.rects = [Rectangle(0, 0, z, Room.dim.x, Room.dim.y, WHITE)
                for z in range(0, Room.dim.z + rects_spacing , rects_spacing)]

    def draw(self, renderer):
        for rect in self.rects:
            rect.draw(renderer)

def main():
    sdl2.ext.init()
    window = sdl2.ext.Window("SURV!", size=(800, 600))
    window.show()
    renderer = sdl2.ext.Renderer(window)

    room = Room()
    p1 = Paddle(Room.dim.x/2 - Paddle.LENGTH_X/2, Room.dim.y/2 - Paddle.LENGTH_Y/2, 0, 0, 0, GREEN)
    p2 = Paddle(Room.dim.x/2 - Paddle.LENGTH_X/2, Room.dim.y/2 - Paddle.LENGTH_Y/2, Room.dim.z, 0, 0, ORANGE)
    ball = Ball(Room.dim.x/2 - Ball.LENGTH_X/2, Room.dim.y/2 - Ball.LENGTH_Y/2, Room.dim.z/2, 0, 0, 0)
    figures = [room, p1, p2, ball]

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
        for figure in figures:
            figure.draw(renderer)

        sdl2.SDL_Delay(10)
        renderer.present()

    return 0

    sdl2.ext.quit()

if __name__ == "__main__":
    sys.exit(main())

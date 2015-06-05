import sys
import os
import sdl2.ext
import sdl2
import ctypes
import random
from enum import Enum

root_dir = os.path.dirname(os.path.abspath(__file__))
resources = sdl2.ext.Resources(os.path.join(root_dir, "resources"))

BLACK = sdl2.ext.Color(0, 0, 0)
WHITE = sdl2.ext.Color(255, 255, 255)
MAGENTA = sdl2.ext.Color(255, 0, 255)
CYAN = sdl2.ext.Color(0, 255, 255)
YELLOW = sdl2.ext.Color(255, 255, 0)
GREEN = sdl2.ext.Color(0, 255, 0)
ORANGE = sdl2.ext.Color(255, 125, 0)
OCEAN = sdl2.ext.Color(0, 125, 255)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
COURT_LENGTH = 2400

CollisionStatus = Enum(
        'CollisionStatus',
        'player_hit computer_hit player_miss computer_miss wall_hit no_collision'
        )
State = Enum(
        'State',
        'menu in_play'
        )

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

    def place(self, x, y, z):
        self.pos.x, self.pos.y, self.pos.z = x, y, z
        self.redraw = True

    def should_redraw(self):
        old_val = self.redraw
        redraw = False
        return old_val

class Rectangle(Figure):
    def __init__(self, x, y, z, len_x, len_y, color):
        super().__init__(x, y, z, len_x, len_y, color)

    def draw(self, renderer):
        """Draws the rect, scaling the width and height and offsetting the x
        and y coordinates according to the the z-coordinate. These operations
        are both linear functions of z"""
        if not super().should_redraw():
            return

        dim_x, dim_y = super().scale_dim()
        x, y = super().scale_pos()
        
        renderer.draw_rect((round(x), round(y), round(dim_x), round(dim_y)),
                self.color)

class Paddle(object):
    dim = Dim2D(120, 90)

    def __init__(self, x, y, z, vel_x, vel_y, color):
        self.pos = Pos3D(x, y, z)
        self.vel = Vel2D(vel_x, vel_y)
        self.rect = Rectangle(x, y, z, Paddle.dim.x, Paddle.dim.y, color)

    def handle_collision(self, room):
        if self.pos.x > room.dim.x - self.dim.x:
            self.pos.x = room.dim.x - self.dim.x
        if self.pos.y > room.dim.y - self.dim.y:
            self.pos.y = room.dim.y - self.dim.y
        self.place(self.pos.x, self.pos.y)

    def draw(self, renderer):
        self.rect.draw(renderer)

    def place(self, x, y):
        self.pos.x, self.pos.y = x, y
        self.rect.place(x, y, self.pos.z)

class Ball(object):
    dim = Dim3D(15, 15, 15)
    start_speed = 20

    def __init__(self, x, y, z, vel_x, vel_y, vel_z, room):
        self.pos = Pos3D(x, y, z)
        self.speed = Ball.start_speed
        self.vel = Vel3D(vel_x, vel_y, vel_z)
        self.rect = Rectangle(0, 0, 0, room.dim.x, room.dim.y, CYAN)
        self.disc = Rectangle(self.pos.x, self.pos.y, self.pos.z,
                Ball.dim.x, Ball.dim.y, MAGENTA)

    def handle_collision(self, paddle_1, paddle_2, room):
        #can be improved by checking intersection between line and plane
        status = CollisionStatus.no_collision
        if self.pos.z <= 0:
            if (self.pos.x > paddle_1.pos.x
                    and self.pos.x + self.dim.x < paddle_1.pos.x + paddle_1.dim.x
                    and self.pos.y > paddle_1.pos.y
                    and self.pos.y + self.dim.y < paddle_1.pos.y + paddle_1.dim.y):
                self.vel.z = self.speed
                status = CollisionStatus.player_hit
            else:
                status = CollisionStatus.player_miss
        elif self.pos.z >= room.dim.z:
            if (self.pos.x > paddle_2.pos.x
                    and self.pos.x + self.dim.x < paddle_2.pos.x + paddle_2.dim.x
                    and self.pos.y > paddle_2.pos.y
                    and self.pos.y + self.dim.y < paddle_2.pos.y + paddle_2.dim.y):
                self.vel.z = -self.speed
                status = CollisionStatus.computer_hit
            else:
                status = CollisionStatus.computer_miss

        if self.pos.x < 0 or self.pos.x + self.dim.x > room.dim.x:
            self.vel.x = -self.vel.x
            status = CollisionStatus.wall_hit

        if self.pos.y < 0 or self.pos.y + self.dim.y > room.dim.y:
            self.vel.y = -self.vel.y
            status = CollisionStatus.wall_hit
        
        return status

    def draw(self, renderer):
        #Draw proper disc!!!
        self.disc.draw(renderer)
        self.rect.draw(renderer)

    def place(self, x, y, z):
        self.pos = Pos3D(x, y, z)
        self.disc.place(self.pos.x, self.pos.y, self.pos.z)
        self.rect.place(0, 0, self.pos.z)

    def move(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        self.pos.z += self.vel.z
        self.disc.place(self.pos.x, self.pos.y, self.pos.z)
        self.rect.place(0, 0, self.pos.z)

class Computer(object):
    speed = 2 
    def __init__(self, paddle, room):
        self.paddle = paddle
        self.vel = Vel2D(0, 0)
        self.serve_pos = Vel2D(0, 0)

    def track(self, target):
        """Moves the paddle towards a given target. Returns true if the paddle is
        on target."""
        diff_x = target.x - (self.paddle.pos.x + self.paddle.dim.x/2)
        diff_y = target.y - (self.paddle.pos.y + self.paddle.dim.y/2)

        if (diff_x > Computer.speed):
            self.vel.x = Computer.speed
        elif (diff_x < -Computer.speed):
            self.vel.x = -Computer.speed
        else:
            self.vel.x = diff_x

        if (diff_y > Computer.speed):
            self.vel.y = Computer.speed
        elif (diff_y < -Computer.speed):
            self.vel.y = -Computer.speed
        else:
            self.vel.y = diff_y

        return (diff_x < 2 and diff_y < 2)

    def move_paddle(self):
        x = self.paddle.pos.x + self.vel.x
        y = self.paddle.pos.y + self.vel.y
        self.paddle.place(x, y)
        

    def catch_ball(self, ball, room):
        """Tracks the ball if it is heading towards the computer,
        otherwise returns to the center."""
        if ball.vel.z > 0:
            self.track(Pos2D(
                    ball.pos.x + ball.dim.x/2,
                    ball.pos.y + ball.dim.y/2))
        else:
            self.track(Pos2D(room.dim.x/2, room.dim.y/2))

    def aim_serve(self, room):
        """Sets the position of the paddle when serving."""
        self.serve_pos.x = random.randint(0, room.dim.x - self.paddle.dim.x)
        self.serve_pos.y = random.randint(0, room.dim.y - self.paddle.dim.y)

    def is_serving(self):
        """Approach serve position. Call aim_serve() first. Returns true
        when ready to serve."""
        return not self.track(Pos2D(self.serve_pos.x, self.serve_pos.y))



class Room(object):
    dim = SCENE_DEFAULT
    def __init__(self):
        rects_spacing = Room.dim.z//8
        self.rects = [Rectangle(0, 0, z, Room.dim.x, Room.dim.y, GREEN)
                for z in range(0, Room.dim.z + rects_spacing , rects_spacing)]

    def draw(self, renderer):
        for rect in self.rects:
            rect.draw(renderer)

def main():
    sdl2.ext.init()
    window = sdl2.ext.Window("SURV!", size=(800, 600))
    window.show()
    renderer = sdl2.ext.Renderer(window)
    sdl2.SDL_SetRelativeMouseMode(True)

    #state = State.in_game

    random.seed()

    room = Room()
    p1 = Paddle(Room.dim.x/2 - Paddle.dim.x/2, Room.dim.y/2 - Paddle.dim.y/2, 0, 0, 0, OCEAN)
    p2 = Paddle(Room.dim.x/2 - Paddle.dim.x/2, Room.dim.y/2 - Paddle.dim.y/2, Room.dim.z, 0, 0, ORANGE)
    ball = Ball(Room.dim.x/2 - Ball.dim.x/2, Room.dim.y/2 - Ball.dim.y/2, Room.dim.z/2, 1, 1, -7, room)
    figures = [room, p1, p2, ball]

    computer = Computer(p2, room)

    def refresh_screen():
        renderer.clear(BLACK)
        for figure in figures:
            figure.draw(renderer)

        sdl2.SDL_Delay(10)
        renderer.present()


    def player_serve():
        while True:
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    return
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_UP:
                        #pause
                        pass
                elif event.type == sdl2.SDL_MOUSEMOTION:
                    p1.place(event.motion.x, event.motion.y)
                    ball.place(p1.pos.x + p1.dim.x/2 - ball.dim.x/2,
                               p1.pos.y + p1.dim.y/2 - ball.dim.y/2,
                               p1.pos.z)
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    ball.vel = Vel3D(0, 0, Ball.start_speed)
                    return
            refresh_screen()

    def computer_serve():
        computer.aim_serve(room)
        while computer.is_serving():
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    return
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_UP:
                        #pause
                        pass
            computer.move_paddle()
            ball.place(p2.pos.x + p2.dim.x/2 - ball.dim.x/2,
                       p2.pos.y + p2.dim.y/2 - ball.dim.y/2,
                       p2.pos.z)
            refresh_screen()
            
    def in_game():
        is_player_serving = True
        player_points = 0
        computer_points = 0

        while True:
            if player_points == 3:
                print("Player wins")
                return
            elif computer_points == 3:
                print("Computer wins")
                return

            if is_player_serving:
                player_serve()
            else:
                computer_serve()
            
            while True:
                events = sdl2.ext.get_events()
                for event in events:
                    if event.type == sdl2.SDL_QUIT:
                        running = False
                        return
                    if event.type == sdl2.SDL_KEYDOWN:
                        if event.key.keysym.sym == sdl2.SDLK_UP:
                            #pause
                            pass
                    elif event.type == sdl2.SDL_MOUSEMOTION:
                        p1.place(event.motion.x, event.motion.y)

                ball.move()
                computer.catch_ball(ball, room)
                computer.move_paddle()
                p1.handle_collision(room)
                p2.handle_collision(room)
                ball_status = ball.handle_collision(p1, p2, room)

                refresh_screen()

                if ball_status == CollisionStatus.computer_miss:
                    is_player_serving = True
                    player_points += 1
                    break
                elif ball_status == CollisionStatus.player_miss:
                    is_player_serving = False
                    computer_points += 1
                    break

    #import pdb; pdb.set_trace()
    in_game()

    return 0

    sdl2.ext.quit()

if __name__ == "__main__":
    sys.exit(main())

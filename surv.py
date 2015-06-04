import sys
import os
import sdl2.ext
import sdl2

root_dir = os.path.dirname(os.path.abspath(__file__))
resources = sdl2.ext.Resources(os.path.join(root_dir, "resources"))

WHITE = sdl2.ext.Color(255, 255, 255)

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)

class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, min_x, min_y, max_x, max_y):
        super(MovementSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
    
    def process(self, world, component_sets):
        for velocity, sprite in component_sets:
            width, height = sprite.size
            sprite.x += velocity.x
            sprite.y += velocity.y

            #could be made simpler
            sprite.x = max(self.min_x, sprite.x)
            sprite.y = max(self.min_y, sprite.y)

            p_max_x = sprite.x + width
            p_max_y = sprite.y + height
            if p_max_x > self.max_x:
                sprite.x = self.max_x - width
            if p_max_y > self.max_y:
                sprite.y = self.max_y - height

class CollisionSystem(sdl2.ext.Applicator):
    def __init__(self, min_x, min_y, max_x, max_y):
        super(CollisionSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.ball = None
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def _overlap(self, item):
        pos, sprite = item
        if sprite == self.ball.sprite:
            return False

        left, top, right, bottom = sprite.area
        b_left, b_top, b_right, b_bottom = self.ball.sprite.area

        return (b_left < right and b_right >left and
                b_top < bottom and b_bottom > top)

    def process(self, world, component_sets):
        col_items = [comp for comp in component_sets if self._overlap(comp)]
        if col_items:
            self.ball.velocity.x = -self.ball.velocity.x

            sprite = col_items[0][1]
            ball_center_y = self.ball.sprite.y + self.ball.sprite.size[1] // 2
            half_height = sprite.size[1] // 2
            step_size = half_height // 10
            degrees = 0.7
            paddle_center_y = sprite.y + half_height

            deflection = (paddle_center_y - ball_center_y) // step_size
            if ball_center_y <= paddle_center_y:
                deflection = -deflection
            self.ball.velocity.y = int(round(deflection*degrees))

        if (self.ball.sprite.y <= self.min_y or
                self.ball.sprite.y + self.ball.sprite.size[1] >= self.max_y):
            self.ball.velocity.y = -self.ball.velocity.y

        if (self.ball.sprite.x <= self.min_x or
                self.ball.sprite.x + self.ball.sprite.size[1] >= self.max_x):
            self.ball.velocity.x = -self.ball.velocity.x

class TrackingAIController(sdl2.ext.Applicator):
    def __init__(self, min_y, max_y):
        super(TrackingAIController, self).__init__()
        self.componenttypes = PlayerData, Velocity, sdl2.ext.Sprite
        self.min_y = min_y
        self.max_y = max_y
        self.ball = None

    def process(self, owrld, component_sets):
        for p_data, velocity, sprite in component_sets:
            if not p_data.ai:
                continue

            center_y = sprite.y + sprite.size[1] // 2
            if self.ball.velocity.x < 0:
                # ball is moving away from AI
                if center_y < self.max_y // 2:
                    velocity.y = 3
                elif center_y > self.max_y // 2:
                    velocity.y = -3
                else:
                    velocity.y = 0
            else:
                b_center_y = self.ball.sprite.y + self.ball.sprite.size[1] // 2
                if b_center_y < center_y:
                    velocity.y = -3
                elif b_center_y > center_y:
                    velocity.y = 3
                else:
                    velocity.y = 0

class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.x = 0
        self.y = 0

class Ball(sdl2.ext.Entity):
    def __init__(self, world, sprite, pos_x = 0, pos_y = 0):
        self.sprite = sprite
        self.sprite.position = pos_x, pos_y
        self.velocity = Velocity()

class PlayerData(object):
    def __init__(self):
        super(PlayerData, self).__init__()
        self.ai = False

class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0, ai=False):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()
        self.playerdata = PlayerData()
        self.playerdata.ai = ai

def main():
    sdl2.ext.init()
    window = sdl2.ext.Window("PONG!", size=(800, 600))
    window.show()


    movement = MovementSystem(0, 0, 800, 600)
    collision = CollisionSystem(0, 0, 800, 600)
    ai_controller = TrackingAIController(0, 600)
    sprite_renderer = SoftwareRenderer(window)

    world = sdl2.ext.World()
    world.add_system(movement)
    world.add_system(collision)
    world.add_system(sprite_renderer)
    world.add_system(ai_controller)

    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    sp_paddle1 = factory.from_color(WHITE, size=(20, 100))
    #cant we use a copy constructor here?
    sp_paddle2 = factory.from_color(WHITE, size=(20, 100))
    sp_ball = factory.from_color(WHITE, size=(20,20))
    
    player1 = Player(world, sp_paddle1, 0, 250)
    player2 = Player(world, sp_paddle2, 780, 250, True)
    ball = Ball(world, sp_ball, 390, 290)
    ball.velocity.x = -3

    collision.ball = ball
    ai_controller.ball = ball

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_UP:
                    player1.velocity.y = -3
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    player1.velocity.y = 3
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    player1.velocity.y = 0

        sdl2.SDL_Delay(10)
        world.process()
        #is this unnecessary?
        window.refresh()

    return 0

    sdl2.ext.quit()

if __name__ == "__main__":
    sys.exit(main())

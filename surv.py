import sys
import os
import sdl2.ext

root_dir = os.path.dirname(os.path.abspath(__file__))
resources = sdl2.ext.Resources(os.path.join(root_dir, "resources"))

def main():
    sdl2.ext.init()

    window = sdl2.ext.Window("Hello, World!", size=(640, 480))
    window.show()

    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    sprite = factory.from_image(resources.get_path("hello.bmp"))
    
    sprite.position = 0, 0
    spriterenderer = factory.create_sprite_render_system(window)
    spriterenderer.render(sprite)

    processor = sdl2.ext.TestEventProcessor()
    processor.run(window)

    sdl2.ext.quit()

if __name__ == "__main__":
    main()

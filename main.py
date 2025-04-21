# Импортируем модули
import json
import pygame as pg
import pytmx
# Инициализируем пайгейм
pg.init()
# Константы
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 80
# Масштаб для увеличения тайлов
TILE_SCALE = 1.5

font = pg.font.Font(None, 36)
# Классы для тайлов
# Платформа
class Platform(pg.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super().__init__()

        self.image = pg.transform.scale(image, (width*TILE_SCALE, height*TILE_SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = x*TILE_SCALE
        self.rect.y = y*TILE_SCALE
# Игрок
class Player(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super().__init__()
        # Создаем картинку для игрока
        self.load_animation()
        self.current_image = 0
        self.current_animation = self.idle_animation_right
        self.image = self.current_animation[self.current_image]

        self.rect = self.image.get_rect()
        self.rect.center = (200, 100)

        self.timer = pg.time.get_ticks()
        self.interval = 200
        # Прямоугольник
        self.rect = self.image.get_rect()
        self.rect.center = (250, 100) # начальная позиция
        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width
        self.map_height = map_height
    def update(self, platforms):
        """
        Перемещение игрока.
        """
        keys = pg.key.get_pressed()
        # Перемещение по горизонтали
        if keys[pg.K_LEFT]:
            self.velocity_x = -20
            self.current_animation = self.run_animation_left
        elif keys[pg.K_RIGHT]:
            self.velocity_x = 20
            self.current_animation = self.run_animation_right
        else:
            if self.current_animation == self.idle_animation_left or self.current_animation == self.run_animation_left or self.current_animation == self.jump_animation_left:
                self.current_animation = self.idle_animation_left
            else:
                self.current_animation = self.idle_animation_right
            self.velocity_x = 0

        new_x = self.rect.x + self.velocity_x

        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x
            
        # Перемещение по вертикали
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        for platform in platforms:
            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False
            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0
            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right

        if keys[pg.K_SPACE] and not self.is_jumping:
            self.jump()

        # Анимация бега
        if self.is_jumping:
            if self.current_animation == self.idle_animation_left or self.current_animation == self.run_animation_left or self.current_animation == self.jump_animation_left:
                self.current_animation = self.jump_animation_left
            else:
                self.current_animation = self.jump_animation_right

        if pg.time.get_ticks() - self.timer >= self.interval:
            self.current_image += 1

            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.timer = pg.time.get_ticks()
            self.image = self.current_animation[self.current_image]

    def jump(self):
        self.velocity_y = -45
        self.is_jumping = True
    def load_animation(self):
        tile_size = 32
        tile_scale = 4
        # Анимация спокойного положения
        self.idle_animation_right = []
        self.num_images = 5

        spritesheet = pg.image.load("sprites/Sprite Pack 3/3 - Robot J5/Idle (32 x 32).png")

        for i in range(self.num_images):
            x = i * tile_size
            y = 0

            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size*tile_scale, tile_scale*tile_size))
            self.idle_animation_right.append(image)
        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        # Анимация бега
        self.run_animation_right = []
        self.num_images = 3

        spritesheet = pg.image.load("sprites/Sprite Pack 3/3 - Robot J5/Running (32 x 32).png")

        for i in range(self.num_images):
            x = i * tile_size
            y = 0

            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size*tile_scale, tile_scale*tile_size))
            self.run_animation_right.append(image)
        # Анимация прыжка
        self.run_animation_left = [pg.transform.flip(image, True, False) for image in self.run_animation_right]


        self.jump_animation_right = []
        self.num_images = 1

        spritesheet = pg.image.load("sprites/Sprite Pack 3/3 - Robot J5/Jumping (32 x 32).png")

        for i in range(self.num_images):
            x = i * tile_size
            y = 0

            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size*tile_scale, tile_scale*tile_size))
            self.jump_animation_right.append(image)
        
        self.jump_animation_left = [pg.transform.flip(image, True, False) for image in self.jump_animation_right]
# Класс "Краб"
class Crab(pg.sprite.Sprite):
    def __init__(self, map_width, map_height, start_pos, final_pos):
        super().__init__()
        self.load_animation()
        self.current_animation = self.animation
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.bottomleft = start_pos
        self.left_edge = start_pos[0]

    def load_animation(self):
        ...
# Создаем класс игры
class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Платформер")
        self.level = 1

        self.camera_x = 0
        self.camera_y = 0

        self.setup()

    def setup(self):
        """
        Функция для перехода на новый уровень и обновления игровых данных.
        """
        # Объявляем переменные
        self.collected_coins = 0
        self.clock = pg.time.Clock()
        self.is_running = False
        # Фон
        self.background = pg.image.load("background.png")
        self.background = pg.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        # Создаем группы спрайтов
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        # Загружаем и обрабатываем карту
        self.tmx_map = pytmx.load_pygame("maps/level1.tmx")

        for layer in self.tmx_map:
            if layer.name == "platforms":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    
                    if tile:
                        platform = Platform(tile, x*self.tmx_map.tilewidth, y*self.tmx_map.tileheight, self.tmx_map.tilewidth, self.tmx_map.tileheight)
                        self.all_sprites.add(platform)
                        self.platforms.add(platform)
        self.map_pixel_width = self.tmx_map.width*TILE_SCALE*self.tmx_map.tilewidth
        self.map_pixel_height = self.tmx_map.height*TILE_SCALE*self.tmx_map.tileheight
        # Создаем персонажа
        self.player = Player(self.map_pixel_width, self.map_pixel_height)
        self.all_sprites.add(self.player)
        # Запускаем игровой цикл
        self.run()

    def run(self):
        self.is_running = True
        while self.is_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            pg.display.flip()
        pg.quit()
        quit()
    def event(self):
        """
        Функция для обработки событий.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
        # Перемещение камеры
        keys = pg.key.get_pressed()

        if keys[pg.K_a]:
            self.camera_x += 30
        if keys[pg.K_d]:
            self.camera_x -= 30
        if keys[pg.K_w]:
            self.camera_y += 30
        if keys[pg.K_s]:
            self.camera_y -= 30
    def update(self):
        """
        Функция для перемещения и измения объектов.
        """
        self.player.update(self.platforms)

        self.camera_x = self.player.rect.x - SCREEN_WIDTH//2
        self.camera_y = self.player.rect.y - SCREEN_HEIGHT//2

        self.camera_x = max(0, min(self.camera_x, self.map_pixel_width - SCREEN_WIDTH))

        self.camera_y = max(0, min(self.camera_y, self.map_pixel_height - SCREEN_HEIGHT))

    def draw(self):
        """
        Функция для отрисовки.
        """
        self.screen.blit(self.background, (0, 0))
        # self.all_sprites.draw(self.screen)

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))

# Точка входа
if __name__ == "__main__":
    game = Game()
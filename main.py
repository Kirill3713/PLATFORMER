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
        self.image = pg.Surface((50, 50))
        self.image.fill("green")
        # Прямоугольник
        self.rect = self.image.get_rect()
        self.rect.center = (200, 100) # начальная позиция
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
        if keys[pg.K_LEFT]:
            self.velocity_x = -10
        elif keys[pg.K_RIGHT]:
            self.velocity_x = 10
        else:
            self.velocity_x = 0

        new_x = self.rect.x + self.velocity_x
        print(new_x), self.velocity_x
        # if 0 <= new_x <= self.map_width - self.rect.width:
        self.rect.x = new_x

# Создаем класс игры
class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Платформер")
        self.level = 1

        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 14

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
        self.map_pixel_width = self.tmx_map.width*TILE_SCALE
        self.map_pixel_height = self.tmx_map.height*TILE_SCALE
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
            self.camera_x += self.camera_speed
        if keys[pg.K_d]:
            self.camera_x -= self.camera_speed
        if keys[pg.K_w]:
            self.camera_y += self.camera_speed
        if keys[pg.K_s]:
            self.camera_y -= self.camera_speed
    def update(self):
        """
        Функция для перемещения и измения объектов.
        """
        self.player.update(self.platforms)
    def draw(self):
        """
        Функция для отрисовки.
        """
        self.screen.blit(self.background, (0, 0))
        # self.all_sprites.draw(self.screen)

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(self.camera_x, self.camera_y))

# Точка входа
if __name__ == "__main__":
    game = Game()
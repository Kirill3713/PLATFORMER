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
# Шрифт
font = pg.font.Font(None, 36)
# Классы для тайлов
# Платформа
class Platform(pg.sprite.Sprite):
    """
    Платформы, из которых состоит земля.
    """
    def __init__(self, image, x, y, width, height):
        super().__init__()

        self.image = pg.transform.scale(image, (width*TILE_SCALE, height*TILE_SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = x*TILE_SCALE
        self.rect.y = y*TILE_SCALE
# Игрок
class Player(pg.sprite.Sprite):
    """
    Персонаж, управляемый игроком.
    """
    def __init__(self, map_width, map_height):
        super().__init__()
        # Создаем картинку для игрока и объявляем переменные
        self.load_animation()
        self.current_image = 0
        self.current_animation = self.idle_animation_right
        self.image = self.current_animation[self.current_image]

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
        # Здоровье
        self.hp = 10
        self.damage_timer = pg.time.get_ticks()
        self.damage_interval = 250

    def update(self, platforms):
        """
        Перемещение игрока.
        """
        keys = pg.key.get_pressed()
        # Перемещение по горизонтали
        if keys[pg.K_LEFT]:
            self.velocity_x = -15
            self.current_animation = self.run_animation_left
        elif keys[pg.K_RIGHT]:
            self.velocity_x = 15
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
        """
        Прыжок.
        """
        self.velocity_y = -45
        self.is_jumping = True
    def load_animation(self):
        """
        Загружаем анимацию.
        """
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
        self.run_animation_left = [pg.transform.flip(image, True, False) for image in self.run_animation_right]

        # Анимация прыжка
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

    def get_damage(self, damage):
        """
        Функция для получения урона.
        """
        if pg.time.get_ticks() - self.damage_timer > self.damage_interval:
            self.hp -= damage
            self.damage_timer = pg.time.get_ticks()

# Класс "Краб"
class Crab(pg.sprite.Sprite):
    """
    Враги.
    """
    def __init__(self, map_width, map_height, start_pos, final_pos):
        super().__init__()
        # Картинка, анимация и нужные переменные
        self.load_animation()
        self.current_animation = self.run_animation
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.bottomleft = start_pos
        self.left_edge = start_pos[0]

        self.final_pos = final_pos[0] + self.image.get_width()
        self.start_pos = start_pos[0]
        self.velocity = 1
        self.rect.x = start_pos[0]
        self.rect.y = start_pos[1]
        self.direction = "right"
        self.interval = 300
        self.timer = pg.time.get_ticks()

        self.velocity_y = 0
        self.gravity = 2

        self.map_width = map_width
        self.map_height = map_height

    def load_animation(self):
        tile_size = 32
        tile_scale = 4
        # Анимация бега
        self.run_animation = []

        image = pg.image.load("sprites/Sprite Pack 2/9 - Snip Snap Crab/Movement_(Flip_image_back_and_forth) (32 x 32).png")

        image = pg.transform.scale(image, (tile_size*tile_scale, tile_scale*tile_size))
        self.run_animation.append(image)
        self.run_animation.append(pg.transform.flip(image, True, False))

    def update(self, platforms):
        """
        Передвижение.
        """
        if self.direction == "right":
            self.velocity = 5
            if self.rect.x >= self.final_pos:
                self.direction = "left"
        else:
            self.velocity = -5
            if self.rect.x <= self.start_pos:
                self.direction = "right"
        new_x = self.rect.x + self.velocity

        if 0 < new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x
        
        # Гравитация
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for platform in platforms:
            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0
            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right

        # Анимация
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()
        
# Класс "Магический огненный шар"
class Ball(pg.sprite.Sprite):
    """
    Оружие игрока.
    """
    def __init__(self, player_rect, direction):
        super().__init__()
        # Картинка и переменные
        self.image = pg.image.load("sprites/ball.png")
        self.image = pg.transform.scale(self.image, (16*TILE_SCALE, 17*TILE_SCALE))
        self.rect = self.image.get_rect()
        self.direction = direction
        if self.direction == "right":
            self.rect.x = player_rect.right
        else:
            self.rect.x = player_rect.left
        self.rect.y = player_rect.centery
        self.velocity = 10
    def update(self):
        """
        Передвижение.
        """
        if self.direction == "right":
            self.rect.x += self.velocity
        else:
            self.rect.x -= self.velocity
# Класс "Монета"
class Coin(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Объявление свойств класса
        self.current_image = 0
        self.load_animation()
        self.image = self.animation[self.current_image]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.interval = 80
        self.timer = pg.time.get_ticks()
    def load_animation(self):
        """
        Анимация.
        """
        self.animation = []

        tile_size = 16
        tile_scale = 3 # Масштаб, коэффициент для пикселя
        self.animation = []
        self.num_images = 5

        spritesheet = pg.image.load("sprites/Coin_Gems/MonedaD.png")

        for i in range(self.num_images):
            x = i * tile_size
            y = 0

            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size*tile_scale, tile_scale*tile_size))
            self.animation.append(image)
    def update(self):
        """
        Передвижение
        """
        if pg.time.get_ticks() - self.timer >= self.interval:
            self.current_image += 1
            if self.current_image >= len(self.animation):
                self.current_image = 0
            self.timer = pg.time.get_ticks()
        self.image = self.animation[self.current_image]
# Класс "Портал"
class Portal(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Объявление свойств класса
        self.current_image = 0
        self.load_animation()
        self.image = self.animation[self.current_image]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.interval = 150
        self.timer = pg.time.get_ticks()
    def load_animation(self):
        """
        Анимация.
        """
        self.animation = []

        tile_size = 64
        tile_scale = 4
        self.animation = []
        self.num_images = 8
        a = 0
        x = 0
        y = 0
        spritesheet = pg.image.load("sprites/Green Portal Sprite Sheet.png")

        for i in range(self.num_images):
            x = tile_size*i

            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.flip(pg.transform.scale(image, (tile_size*tile_scale, tile_scale*tile_size)), True, False)
            self.animation.append(image)

    def update(self):
        """
        Передвижение
        """
        if pg.time.get_ticks() - self.timer >= self.interval:
            self.current_image += 1
            if self.current_image >= len(self.animation):
                self.current_image = 0
            self.timer = pg.time.get_ticks()
        self.image = self.animation[self.current_image]
        # self.rect = self.image.get_rect()
# Класс иголок
class Barrier(pg.sprite.Sprite):
    """
    Иглы.
    """
    def __init__(self, x, y):
        super().__init__()
        # Картинка, анимация и нужные переменные
        self.image = pg.image.load("maps/tileset/PNG/Tiles/tile110.png")
        self.image = pg.transform.scale(self.image, (48*TILE_SCALE, 48*TILE_SCALE))
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

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
        self.mode = "game"
        # Фон
        self.background = pg.image.load("background.png")
        self.background = pg.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        # Создаем группы спрайтов
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.balls = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.portals = pg.sprite.Group()
        self.barriers = pg.sprite.Group()
        # Загружаем и обрабатываем карту
        self.tmx_map = pytmx.load_pygame(f"maps/level{self.level}.tmx")
        # Заполняем экран платформами, монетами и порталами
        for layer in self.tmx_map:
            if layer.name == "platforms":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        platform = Platform(tile, x*self.tmx_map.tilewidth, y*self.tmx_map.tileheight, self.tmx_map.tilewidth, self.tmx_map.tileheight)
                        self.all_sprites.add(platform)
                        self.platforms.add(platform)
            if layer.name == "coins":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        coin = Coin(x*self.tmx_map.tilewidth*TILE_SCALE, y*self.tmx_map.tileheight*TILE_SCALE)
                        self.all_sprites.add(coin)
                        self.coins.add(coin)
            if layer.name == "portal":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        portal = Portal(x*self.tmx_map.tilewidth*TILE_SCALE, y*self.tmx_map.tileheight*TILE_SCALE)
                        self.all_sprites.add(portal)
                        self.portals.add(portal)
            if layer.name == "barrier":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        barrier = Barrier(x*self.tmx_map.tilewidth*TILE_SCALE, y*self.tmx_map.tileheight*TILE_SCALE)
                        self.barriers.add(barrier)
                        self.all_sprites.add(barrier)
        self.map_pixel_width = self.tmx_map.width*TILE_SCALE*self.tmx_map.tilewidth
        self.map_pixel_height = self.tmx_map.height*TILE_SCALE*self.tmx_map.tileheight
        # Создаем персонажа
        self.player = Player(self.map_pixel_width, self.map_pixel_height)
        self.all_sprites.add(self.player)
        # Создаем врага
        self.enemies = pg.sprite.Group()
        with open(f"maps/level{self.level}_enemies.json", "r", encoding="utf-8") as json_file:
            self.data = json.load(json_file)
            for enemy in self.data["enemies"]:
                if enemy["name"] == "Crab":
                    x1 = enemy["start_pos"][0]*self.tmx_map.tilewidth*TILE_SCALE
                    y1 = enemy["start_pos"][1]*self.tmx_map.tileheight*TILE_SCALE

                    x2 = enemy["final_pos"][0]*self.tmx_map.tilewidth*TILE_SCALE
                    y2 = enemy["final_pos"][1]*self.tmx_map.tileheight*TILE_SCALE

                    crab = Crab(self.map_pixel_width, self.map_pixel_height, [x1, y1], [x2, y2])
                    self.all_sprites.add(crab)
                    self.enemies.add(crab)
        # Запускаем игровой цикл
        self.run()

    def run(self):
        """
        Игровой цикл.
        """
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
            if event.type == pg.KEYDOWN:
                if self.mode == "game over":
                    self.setup()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    # Добавляем шар
                    if self.player.current_animation == self.player.idle_animation_left or self.player.current_animation == self.player.run_animation_left or self.player.current_animation == self.player.jump_animation_left:
                        direction = "left"
                    else:
                        direction = "right"
                    self.ball = Ball(self.player.rect, direction)
                    self.balls.add(self.ball)
                    self.all_sprites.add(self.ball)
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
        # Блокируем update, если режим равен проигрышу
        if self.mode == "game over": return
        # Updatим игрока, шары, монеты, врагов, порталы
        self.player.update(self.platforms)
        if self.player.rect.y >= self.map_pixel_height:
            self.mode = "game over"
            self.player.hp = 0

        for ball in self.balls:
            ball.update()
            if ball.rect.x >= self.map_pixel_width or ball.rect.x <= 0:
                ball.kill()

        pg.sprite.groupcollide(self.balls, self.enemies, True, True)
        if self.level != 3:
            pg.sprite.groupcollide(self.balls, self.platforms, True, False)
        else:
            pg.sprite.groupcollide(self.balls, self.platforms, True, True)
        for coin in self.coins:
            coin.update()

        for enemy in self.enemies.sprites():
            enemy.update(self.platforms)
            if pg.sprite.collide_mask(self.player, enemy):
                self.player.get_damage(1)
                if self.player.hp <= 0:
                    self.mode = "game over"

        for barrier in self.barriers.sprites():
            if pg.sprite.collide_mask(self.player, barrier):
                self.player.get_damage(3)
                if self.player.hp <= 0:
                    self.mode = "game over"

        for portal in self.portals:
            portal.update()
        # Собранные монеты
        hits = pg.sprite.spritecollide(self.player, self.coins, True)
        for hit in hits:
            self.collected_coins += 1
        # Переход на новый уровень
        if pg.sprite.spritecollide(self.player, self.portals, False):
            self.level += 1
            self.setup()
        # Обновляем карту
        self.camera_x = self.player.rect.x - SCREEN_WIDTH//2
        self.camera_y = self.player.rect.y - SCREEN_HEIGHT//2

        self.camera_x = max(0, min(self.camera_x, self.map_pixel_width - SCREEN_WIDTH))

        self.camera_y = max(0, min(self.camera_y, self.map_pixel_height - SCREEN_HEIGHT))

    def draw(self):
        """
        Функция для отрисовки.
        """
        # Фон
        self.screen.blit(self.background, (0, 0))
        # Отрисовка всех спрайтов
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))
        # Полоска здоровья
        pg.draw.rect(self.screen, pg.Color("green"), pg.Rect(50, 50, self.player.hp*10, 20))
        pg.draw.rect(self.screen, pg.Color("black"), pg.Rect(50, 50, 100, 20), 1)
        # Счетчик монет
        counter = pg.font.Font(None, 50).render(str(self.collected_coins), True, "blue")
        text_rect = counter.get_rect()
        text_rect.center = (55, 100)
        self.screen.blit(counter, text_rect)
        # Проигрыш
        if self.mode == "game over":
            game_over_text = pg.font.Font(None, 30).render("Game over", True, "black")
            text_rect = game_over_text.get_rect()
            text_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            self.screen.blit(game_over_text, text_rect)
# Точка входа
if __name__ == "__main__":
    game = Game()
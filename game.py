import sys
import time
import pygame
import random as rd

WIDTH, HEIGHT = 1920, 1080

BLACK = (0, 0, 0)
RED = (255, 0, 0)

FPS = 100
FALLING_SPEED = 100
GRAVITY = 0.75
clock = pygame.time.Clock()

move, moving_to_the_left, moving_to_the_right = False, False, False
SCROLL_MAX = WIDTH // 2 - 50
screen_scroll = 0
bg_scroll = 0
scale = 9

start_game = False
pygame.init()
pygame.font.init()
pygame.mixer.init()

pygame.display.set_caption('the long wild road')
font = pygame.font.Font('fonts/CrackersBiscuit.otf', 63)

counter = 0
time_delay = 1000
timer_event = pygame.USEREVENT + 1
pygame.time.set_timer(timer_event, time_delay)

one_board_image = pygame.image.load('pics/one_board.png')
one_board_image = pygame.transform.scale(one_board_image,
                                         (one_board_image.get_width() // (0.2 * scale),
                                          one_board_image.get_height() // (0.2 * scale)))
noose_image = pygame.image.load('pics/noose.png')
noose_image = pygame.transform.scale(noose_image,
                                     (noose_image.get_width() // (2 * scale),
                                      noose_image.get_height() // (2 * scale)))
unit_of_health = pygame.image.load('pics/health.png')
unit_of_health = pygame.transform.scale(unit_of_health,
                                        (unit_of_health.get_width() // (1.2 * scale),
                                         unit_of_health.get_height() // (1.2 * scale)))
bullets_in_inventory = pygame.image.load('pics/one_bullet.png')
bullets_in_inventory = pygame.transform.scale(bullets_in_inventory,
                                              (bullets_in_inventory.get_width() // (0.4 * scale),
                                               bullets_in_inventory.get_height() // (0.4 * scale)))
a_bag_of_money = pygame.image.load('pics/a_bag_of_money.png')
a_bag_of_money = pygame.transform.scale(a_bag_of_money,
                                        (a_bag_of_money.get_width() // (0.4 * scale),
                                         a_bag_of_money.get_height() // (0.4 * scale)))
magic_whiskey = pygame.image.load('pics/magic_whiskey.png')
magic_whiskey = pygame.transform.scale(magic_whiskey,
                                       (magic_whiskey.get_width() // scale,
                                        magic_whiskey.get_height() // scale))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.image.load('pics/west_2.png').convert()
bg_width, bg_height = background.get_size()

bad_guys_group = pygame.sprite.Group()
objects_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
nooses_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def sound(position):
    if not pygame.mixer.music.get_busy():
        if position == 0:
            pygame.mixer.music.load('music/The_Good_the_Bad_and_the_Ugly.mp3')
        elif position == 1:
            pygame.mixer.music.load('music/The_Animals_House_of_Rising_Sun.mp3')
        pygame.mixer.music.play(-1, 0.0, 3000)


def start_screen():
    start_bg = pygame.transform.scale(pygame.image.load('pics/menu_.png'), (WIDTH, HEIGHT))
    screen.blit(start_bg, (0, 0))

    enter_image = pygame.image.load('pics/enter.png')
    enter_image = pygame.transform.scale(enter_image, (250, 250))
    screen.blit(enter_image, (1720, 880))
    start_font = pygame.font.Font('fonts/CrackersBiscuit.otf', 96)
    start = start_font.render('to the wild west', False, BLACK)
    screen.blit(start, (900, 1000))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                terminate()
            if event.key == pygame.K_RETURN:
                pygame.mixer.music.stop()
                hero.alive = True
                hero.health = 4
                hero.count_of_bullets = 10
                return True
    return False


def game_screen():
    screen.blit(background, (0 - bg_scroll, 0))

    screen.blit(one_board_image, (0, 0))
    screen.blit(one_board_image, (WIDTH // 2 - (one_board_image.get_width() // 2), 0))
    screen.blit(one_board_image, (WIDTH - one_board_image.get_width(), 0))

    status('bullets', BLACK, 110, 160)
    screen.blit(bullets_in_inventory, (95, 10))
    status(f'  x  {hero.count_of_bullets}', BLACK, 200, 60)

    status('health', BLACK, WIDTH // 2 - (one_board_image.get_width() // 2) + 120, 160)
    for pin in range(hero.health):
        screen.blit(unit_of_health, (WIDTH // 2 - (one_board_image.get_width() // 2) + 80 + (pin * 80), 40))

    status('money', BLACK, WIDTH - one_board_image.get_width() + 150, 160)
    screen.blit(a_bag_of_money, (WIDTH - one_board_image.get_width() + 120, 10))
    status(f'  x  {hero.money}', BLACK, WIDTH - one_board_image.get_width() + 200, 60)


def status(text, color, x, y):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))


class Objects(pygame.sprite.Sprite):
    def __init__(self, this_item, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.scale = 5
        self.this_item = this_item
        self.image = pygame.transform.scale(pygame.image.load(f'pics/{this_item}.png'),
                                            (pygame.image.load(
                                                f'pics/{this_item}.png').get_width() // self.scale,
                                             pygame.image.load(
                                                 f'pics/{this_item}.png').get_height() // self.scale))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_mask(self, hero):
            hero.update_inventory(self.this_item)
            self.kill()


class Noose(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.scale = 5
        self.image = noose_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pixels_per_second = 100
        self.last_update = int(time.time() * 1000.0)

    def update(self):

        time_now = int(time.time() * 1000.0)
        time_change = time_now - self.last_update
        if self.pixels_per_second > 0 and time_change > 0:
            distance_moved = time_change * self.pixels_per_second / 1000
            now_x, now_y = self.rect.center
            updated_y = now_y + distance_moved
            self.rect.center = (now_x + screen_scroll, updated_y)
            self.last_update = time_now
        if pygame.sprite.collide_mask(hero, self):
            if hero.alive:
                hero.health -= 1
                self.kill()
                if hero.health == 0:
                    hero.alive = False
                    start_game = False
                    pygame.mixer.music.stop()
                    sound(0)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, back):
        pygame.sprite.Sprite.__init__(self)
        self.back = back
        self.speed = 20
        self.scale = 15
        self.image = pygame.transform.flip(pygame.image.load('pics/bullet.png').convert_alpha(), back, False)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // self.scale,
                                                         self.image.get_height() // self.scale))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        if self.back:
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

        if self.rect.x < 0 or self.rect.x + self.rect.w > WIDTH:
            self.kill()

        if pygame.sprite.collide_mask(hero, self):
            if hero.alive:
                hero.health -= 1
                if hero.health == 0:
                    hero.alive = False
                    start_game = False
                    pygame.mixer.music.stop()
                    sound(0)
            self.kill()
        for bandit in bad_guys_group:
            if pygame.sprite.collide_mask(bandit, self):
                if bandit.alive:
                    bandit.health -= 1
                    if bandit.health == 0:
                        bandit.alive = False
                        bandit.kill()
                self.kill()


class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, count_of_bullets):
        pygame.sprite.Sprite.__init__(self)

        self.alive = True
        self.health = 4
        self.money = 0
        self.max_health = self.health
        self.count_of_bullets = count_of_bullets

        self.back = False
        self.jumping = False
        self.in_air = False

        self.speed_x = speed
        self.speed_y = 0

        self.animation_time = 3
        self.current_time = 0

        self.index = 0

        self.scale = 4
        self.images = []
        self.stand = []
        self.stand.append(pygame.transform.scale(pygame.image.load('pics/clint/C_4.png'),
                                                 (pygame.image.load('pics/clint/C_4.png').get_width()
                                                  // self.scale,
                                                  pygame.image.load('pics/clint/C_4.png').get_height() // self.scale)))
        self.stand.append(pygame.transform.scale(pygame.image.load('pics/clint/C_5.png'),
                                                 (pygame.image.load('pics/clint/C_5.png').get_width()
                                                  // self.scale,
                                                  pygame.image.load('pics/clint/C_5.png').get_height() // self.scale)))
        self.stand.append(pygame.transform.scale(pygame.image.load('pics/clint/C_4.png'),
                                                 (pygame.image.load('pics/clint/C_4.png').get_width()
                                                  // self.scale,
                                                  pygame.image.load('pics/clint/C_4.png').get_height() // self.scale)))

        self.images.append(pygame.transform.scale(pygame.image.load('pics/clint/C_0.png'),
                                                  (pygame.image.load('pics/clint/C_0.png').get_width() //
                                                   self.scale,
                                                   pygame.image.load('pics/clint/C_0.png').get_height() // self.scale)))
        self.images.append(pygame.transform.scale(pygame.image.load('pics/clint/C_3.png'),
                                                  (pygame.image.load('pics/clint/C_3.png').get_width()
                                                   // self.scale,
                                                   pygame.image.load('pics/clint/C_3.png').get_height() // self.scale)))
        self.images.append(pygame.transform.scale(pygame.image.load('pics/clint/C_4.png'),
                                                  (pygame.image.load('pics/clint/C_4.png').get_width()
                                                   // self.scale,
                                                   pygame.image.load('pics/clint/C_4.png').get_height() // self.scale)))
        self.images.append(pygame.transform.scale(pygame.image.load('pics/clint/C_5.png'),
                                                  (pygame.image.load('pics/clint/C_5.png').get_width()
                                                   // self.scale,
                                                   pygame.image.load('pics/clint/C_5.png').get_height() // self.scale)))

        self.image = self.images[self.index]

        self.image = pygame.transform.scale(self.image, (self.image.get_width() // self.scale,
                                                         self.image.get_height() // self.scale))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):

        screen_scroll = 0
        dx, dy = 0, 0
        if moving_left:
            dx = -self.speed_x
            self.back = True
        if moving_right:
            dx = self.speed_x
            self.back = False
        if self.jumping:
            self.in_air = True
            self.jumping = False
            self.speed_y = -10
        if self.speed_y > 10:
            self.speed_y = 10
        if self.speed_y <= 0:
            self.image = pygame.transform.scale(pygame.image.load('pics/clint/C_jump.png'),
                                                (pygame.image.load('pics/clint/C_jump.png').get_width() // self.scale,
                                                 pygame.image.load('pics/clint/C_jump.png').get_height() // self.scale))

        self.speed_y += GRAVITY
        dy += self.speed_y

        if self.rect.bottom + dy > 700:
            dy = 700 - self.rect.bottom
            self.in_air = False

        self.rect.x += dx
        self.rect.y += dy

        if (self.rect.right > WIDTH - SCROLL_MAX and bg_scroll < bg_width) or self.rect.left < SCROLL_MAX:
            self.rect.x -= dx
            screen_scroll = -dx

        return screen_scroll

    def update_animation_moving(self):
        self.index += 1
        if self.current_time >= self.animation_time:
            self.current_time = 0
        self.index = (self.index + 1) % len(self.images)
        self.image = self.images[self.index]

    def update_animation_standing(self):
        self.index += 1
        if self.current_time >= self.animation_time:
            self.current_time = 0
        self.index = (self.index + 1) % len(self.stand)
        self.image = self.stand[self.index]

    def update_inventory(self, element):
        if element == 'water':
            hero.health += 1
            if hero.health > hero.max_health:
                hero.health = hero.max_health

        elif element == 'magic_whiskey':
            hero.health = hero.max_health

        elif element == 'a_bag_of_money':
            hero.money += 1

        elif element == 'one_bullet':
            hero.count_of_bullets += 1

    def shoot(self):
        if self.count_of_bullets > 0:
            if self.back:
                bullet = Bullet(self.rect.centerx - self.rect.size[0] * 0.4,
                                self.rect.centery + self.rect.size[1] // 1.35,
                                self.back)
            else:
                bullet = Bullet(self.rect.centerx + self.rect.size[0] * 3.6,
                                self.rect.centery + self.rect.size[1] // 1.35,
                                self.back)
            self.count_of_bullets -= 1
            bullets_group.add(bullet)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.back, False), self.rect)


class CowboysAndNotOnly(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)

        self.alive = True
        self.waiting = False
        self.waiting_counter = 0
        self.view = pygame.Rect(0, 0, 600, 50)
        self.health = rd.randint(3, 50)
        self.count_of_bullets = 1000

        self.direction = 1
        self.passed = 0
        self.moving_left, self.moving_right = False, False

        self.speed_x = speed
        self.speed_y = 0

        self.animation_time = 3
        self.current_time = 0
        self.index = 0
        self.scale = 4

        self.images = []
        self.stand = []

        self.images.append(pygame.transform.scale(pygame.image.load('pics/cowboy/2_5_bad_guy.png'),
                                                  (pygame.image.load('pics/cowboy/2_5_bad_guy.png').get_width()
                                                   // self.scale,
                                                   pygame.image.load(
                                                       'pics/cowboy/2_5_bad_guy.png').get_height() // self.scale)))

        self.images.append(pygame.transform.scale(pygame.image.load('pics/cowboy/2_bad_guy.png'),
                                                  (pygame.image.load('pics/cowboy/2_bad_guy.png').get_width()
                                                   // self.scale,
                                                   pygame.image.load(
                                                       'pics/cowboy/2_bad_guy.png').get_height() // self.scale)))
        self.images.append(pygame.transform.scale(pygame.image.load('pics/cowboy/1_4_bad_guy.png'),
                                                  (pygame.image.load('pics/cowboy/1_4_bad_guy.png').get_width()
                                                   // self.scale,
                                                   pygame.image.load(
                                                       'pics/cowboy/1_4_bad_guy.png').get_height() // self.scale)))

        self.stand.append(pygame.transform.scale(pygame.image.load('pics/cowboy/1_5_bad_guy.png'),
                                                 (pygame.image.load('pics/cowboy/1_5_bad_guy.png').get_width()
                                                  // self.scale,
                                                  pygame.image.load(
                                                      'pics/cowboy/1_5_bad_guy.png').get_height() // self.scale)))
        self.stand.append(pygame.transform.scale(pygame.image.load('pics/cowboy/1_4_bad_guy.png'),
                                                 (pygame.image.load('pics/cowboy/1_4_bad_guy.png').get_width()
                                                  // self.scale,
                                                  pygame.image.load(
                                                      'pics/cowboy/1_4_bad_guy.png').get_height() // self.scale)))
        self.stand.append(pygame.transform.scale(pygame.image.load('pics/cowboy/1_bad_guy.png'),
                                                 (pygame.image.load('pics/cowboy/1_bad_guy.png').get_width()
                                                  // self.scale,
                                                  pygame.image.load('pics/cowboy/1_bad_guy.png').get_height()
                                                  // self.scale)))

        self.image = self.images[self.index]

        self.image = pygame.transform.scale(self.image, (self.image.get_width() // self.scale,
                                                         self.image.get_height() // self.scale))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        dx, dy = 0, 0
        if moving_left:
            dx = -self.speed_x
            self.direction = -1
        if moving_right:
            dx = self.speed_x
            self.direction = 1

        self.rect.x += dx

    def update_animation_moving(self):
        self.index += 1
        if self.current_time >= self.animation_time:
            self.current_time = 0
        self.index = (self.index + 1) % len(self.images)
        self.image = self.images[self.index]

    def update_animation_standing(self):
        self.index += 1
        if self.current_time >= self.animation_time:
            self.current_time = 0
        self.index = (self.index + 1) % len(self.stand)
        self.image = self.stand[self.index]

    def shoot(self, shoot_down):
        if shoot_down == 5:
            if self.direction == -1:
                bullet = Bullet(self.rect.centerx - self.rect.size[0] * 0.6,
                                self.rect.centery + self.rect.size[1] // 2.3,
                                True)
            else:
                bullet = Bullet(self.rect.centerx + self.rect.size[0] * 2.6,
                                self.rect.centery + self.rect.size[1] // 2.3,
                                False)

            bullets_group.add(bullet)

    def action(self):
        if self.alive:

            if rd.randint(1, 100) == 30:
                self.waiting = True
                self.waiting_counter = 0

            if self.view.colliderect(hero.rect):
                self.update_animation_standing()
                self.shoot(rd.randint(1, 10))
            else:

                if not self.waiting:
                    if self.direction == -1:
                        self.moving_left = True
                    else:
                        self.moving_left = False
                    self.passed += 1
                    self.moving_right = not self.moving_left
                    self.move(self.moving_left, self.moving_right)
                    self.update_animation_moving()

                    self.view.center = (self.rect.centerx + 80 * self.direction, self.rect.centery)

                    if self.passed > 50:
                        self.passed *= -1
                        self.direction *= -1

                    if self.rect.x <= 0:
                        self.direction = 1
                        self.passed = 0
                    elif self.rect.x >= WIDTH - self.rect.width:
                        self.direction = -1
                        self.passed = 0
                else:
                    self.update_animation_standing()
                    self.waiting_counter += 1
                    if self.waiting_counter > 50:
                        self.waiting = False

    def draw(self):
        self.rect.x += screen_scroll

        if self.direction == -1:
            screen.blit(pygame.transform.flip(self.image, False, False), self.rect)
        else:
            screen.blit(pygame.transform.flip(self.image, True, False), self.rect)


def update_objects():
    for stuff in range(rd.randint(1, 10)):
        item = Objects('water', rd.randint(10, 4000), rd.randint(10, 700))
        objects_group.add(item)
    for stuff in range(rd.randint(1, 20)):
        item = Objects('one_bullet', rd.randint(10, 4000), rd.randint(10, 700))
        objects_group.add(item)
    for stuff in range(rd.randint(1, 10)):
        item = Objects('a_bag_of_money', rd.randint(10, 4000), rd.randint(10, 700))
        objects_group.add(item)
    for stuff in range(rd.randint(1, 10)):
        item = Objects('magic_whiskey', rd.randint(10, 4000), rd.randint(10, 700))
        objects_group.add(item)


update_objects()

hero = Hero(500, 700, 10, 10)

first_bad_guy = CowboysAndNotOnly(800, 700, 3)
second_bad_guy = CowboysAndNotOnly(1500, 700, 8)
third_bad_guy = CowboysAndNotOnly(2600, 700, 15)
bad_guys_group.add(first_bad_guy, second_bad_guy, third_bad_guy)

running = True
while running:
    dt = clock.tick(FPS) / 1000
    if not start_game:
        sound(0)
        start_game = start_screen()
    else:
        if hero.alive:
            sound(1)
            game_screen()

            falling_noose = rd.randint(1, 90)
            if falling_noose == 27:
                noose = Noose(rd.randint(10, WIDTH), 0)
                nooses_group.add(noose)

            for noose in nooses_group:
                noose.update()

            for guy in bad_guys_group:
                guy.action()
                guy.update()
                guy.draw()

            if move:
                hero.update_animation_moving()
            else:
                hero.update_animation_standing()

            screen_scroll = hero.move(moving_to_the_left, moving_to_the_right)
            if (bg_scroll - screen_scroll <= WIDTH + SCROLL_MAX) and (bg_scroll - screen_scroll >= 0):
                bg_scroll -= screen_scroll

            hero.draw()

            objects_group.update()
            bullets_group.update()
            nooses_group.update()

            objects_group.draw(screen)
            bullets_group.draw(screen)
            nooses_group.draw(screen)
        else:
            sound(0)
            start_game = start_screen()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                hero.shoot()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                hero.jumping = True
            if event.key == pygame.K_ESCAPE:
                terminate()

            if event.key == pygame.K_LEFT:
                move = True
                moving_to_the_left = True
            if event.key == pygame.K_RIGHT:
                move = True
                moving_to_the_right = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                hero.jumping = False
            if event.key == pygame.K_ESCAPE:
                terminate()
            if event.key == pygame.K_LEFT:
                move = False
                moving_to_the_left = False
            if event.key == pygame.K_RIGHT:
                move = False
                moving_to_the_right = False
        elif event.type == timer_event:
            counter += 1
            if counter % 10 == 0:
                for obj in objects_group:
                    obj.kill()
                update_objects()

    pygame.display.update()
pygame.quit()

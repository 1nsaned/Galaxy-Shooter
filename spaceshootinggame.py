import arcade
import math 
import random
import os

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Galaxy Shooter"

PLAYER_SCALE = 0.3
PLAYER_SPEED = 5
PLAYER_TURN_SPEED = 3
PLAYER_SHOOT_COOLDOWN = 0.2

BULLET_SPEED = 10
BULLET_SCALE = 0.8

ENEMY_SPWAN_RATE = 1
ENEMY_SPEED_MIN = 1
ENEMY_SPEED_MAX = 3
ENEMY_SCALE = 0.3

ENEMY_TYPES = ["normal", "shooter"]
ENEMY_SHOOT_COOLDOWN = 2.0
ENEMY_BULLET_SPEED = 5
ENEMY_BULLET_COLOR = arcade.color.RED

PARTICLE_COUNT = 5
PARTICLE_SPEED = 6
PARTICLE_FADE_RATE = 4


class Powerup:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.radius = 20
        self.speed_y = -1

        if power_type == "rapid fire":
            self.color = arcade.color.CYAN
        elif power_type == "shield":
            self.color = arcade.color.BLUE
        else:
            self.color = arcade.color.GREEN

    def update(self):
        self.y += self.speed_y

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)
        if self.type == "rapid_fire":
            arcade.draw_text("💥", self.x - 6, self.y -
                             6, arcade.color.WHITE,12)
        elif self.type == "shield":
            arcade.draw_text("🔰", self.x - 6, self.y -
                             6, arcade.color.WHITE,12)
        else:
            arcade.draw_text("💛", self.x - 6, self.y -
                             6, arcade.color.WHITE,12) 

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(3, 8)
        self.color = random.choice([
            arcade.color.YELLOW,
            arcade.color.ORANGE,
            arcade.color.RED
        ])
        self.speed_x = random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
        self.speed_y = random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
        self.alpha = 255

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.alpha -= PARTICLE_FADE_RATE
        return self.alpha > 0
    
    def draw(self):
        arcade.draw_circle_filled(
            self.x, self.y, self.size,
            (*self.color[ :3], int(self.alpha)))
        

class EnemyBullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = ENEMY_BULLET_SPEED
        self.radius = 6
        self.color = ENEMY_BULLET_COLOR
    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

    def draw(self):
        arcade.draw_circle_filled(
            self.x, self.y, self.radius, self.color
            )

    def is_off_screen(self):
         return (self.x < 0 or self.x > SCREEN_WIDTH or
                    self.y < 0 or self.y > SCREEN_HEIGHT)
        

class Enemy:
    def __init__(self):
        side = random.choice(["top", "right", "bottom", "left"])
        if side == "top":
            self.x = random.uniform(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT + 20
        elif side == "right":
            self.x = SCREEN_WIDTH + 20
            self.y = random.uniform(0, SCREEN_HEIGHT)
        elif side == "bottom":
            self.x = random.uniform(0, SCREEN_WIDTH)
            self.y = -20
        else:
            self.x = -20
            self.y = random.uniform(0, SCREEN_HEIGHT)

        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.angle = 0
        
        self.radius = 150 * ENEMY_SCALE
        self.health = 3
        self.max_health = 3
        self.enemy_type = random.choice(["normal", "shooter"])
        if self.enemy_type == "normal":
            self.texture = arcade.load_texture(
                 r"C:\Users\Chandradev\.vscode\spaceshooter_ByJanaChumi\spaceshooter_ByJanaChumi\items\14.png"
            )
        else:
            self.texture = arcade.load_texture(
                r"C:\Users\Chandradev\.vscode\spaceshooter_ByJanaChumi\spaceshooter_ByJanaChumi\items\15.png"
            )
        self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
        self.enemy_bullets = []

    def update(self, player_x, player_y, delta_time):
        dx = player_x - self.x
        dy = player_y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))

        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        if self.enemy_type == "shooter":
            self.shoot_cooldown -= delta_time
            if self.shoot_cooldown <= 0:
                self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
                return EnemyBullet(self.x, self.y, self.angle)
        return None

    def draw(self):
        arcade.draw_texture_rect(
            self.texture,
            arcade.XYWH(self.x, self.y, 60,60),
            angle=self.angle - 90
        )
        self.draw_health_bar()

    def draw_health_bar(self):
        if self.health <= self.max_health:
            bar_width = 50
            bar_height = 6
            health_percentage = self.health / self.max_health
            health_width = health_percentage * bar_width
            bar_x = self.x - bar_width / 2
            bar_y = self.y + self.radius + 20

            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + bar_width,
                bar_y, bar_y + bar_height,
                arcade.color.RED)
            
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + health_width,
                bar_y, bar_y + bar_height,
                arcade.color.GREEN) 
                                         
            arcade.draw_lrbt_rectangle_outline(
                bar_x, bar_x + bar_width,
                bar_y, bar_y + bar_height,
                arcade.color.WHITE, 1)
                
            
    def is_of_screen(self):
        return (self.x < -50 or self.x > SCREEN_WIDTH + 50 or
                self.y < -50 or self.y > SCREEN_HEIGHT + 50)
    
class BossBullet:
    def __init__(self, x, y, angle, is_big=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.is_big = is_big
        self.speed = 7
        self.damage = 999 if is_big else 30

        if is_big:
            self.radius = 12
            self.color = arcade.color.YELLOW
        else:
            self.radius = 6
            self.color = arcade.color.ORANGE_RED

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)

    def is_off_screen(self):
        return(self.x < 0 or self.x > SCREEN_WIDTH or
               self.y < 0 or self.y > SCREEN_HEIGHT)
    
class Boss:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 + random.uniform(-200, 200)
        self.y = SCREEN_HEIGHT + 100

        self.speed = 2
        self.angle = 0
        self.radius = 150 * ENEMY_SCALE * 3
        self.health = 100
        self.max_health =  100

        self.normal_shoot_cooldown = 0
        self.big_shoot_cooldown = 0
        self.damage_flash_timer = 0
        self.flashing = False

        self.color = arcade.color.ORANGE

    def take_damage(self):
        self.health -= 1
        self.damage_flash_timer = 0.3
        self.flashing = True
        return self.health <= 0
    
    def update(self, player_x, player_y, delta_time):
        dx = player_x - self.x
        dy = player_y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))

        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

        self.normal_shoot_cooldown -= delta_time
        if self.damage_flash_timer <= 0:
            self.flashing = False

    def shoot_normal(self):
        if self.normal_shoot_cooldown <= 0:
            bullet_x = self.x + \
                math.cos(math.radians(self.angle)) * self.radius
            bullet_y = self.y + \
                math.sin(math.radians(self.angle)) * self.radius
            self.normal_shoot_cooldown = 1.5
            return BossBullet(bullet_x, bullet_y, self.angle, is_big=False)
        return None
    
    def shoot_big(self):
        if self.normal_shoot_cooldown <= 0:
            bullet_x = self.x + \
                math.cos(math.radians(self.angle)) * self.radius
            bullet_y = self.y + \
                math.sin(math.radians(self.angle)) * self.radius
            self.big_shoot_cooldown = 8.0
            return BossBullet(bullet_x, bullet_y, self.angle, is_big=True)
        return None
    
    def draw(self):
        if self.flashing:
            draw_color = arcade.color.WHITE
        else:
            draw_color = self.color

        points = [
            (self.x + math.cos(math.radians(self.angle)) * self.radius * 1.5,
             self.y + math.sin(math.radians(self.angle)) * self.radius * 1.5),
            (self.x + math.cos(math.radians(self.angle + 90)) * self.radius,
             self.y + math.sin(math.radians(self.angle + 90)) * self.radius),
            (self.x + math.cos(math.radians(self.angle + 180)) * self.radius * 1.5,
             self.y + math.sin(math.radians(self.angle + 180)) * self.radius * 1.5),
            (self.x + math.cos(math.radians(self.angle + 270)) * self.radius,
             self.y + math.sin(math.radians(self.angle + 270)) * self.radius)
        ]
        arcade.draw_texture_rect(
            arcade.load_texture(
                r"C:\Users\Chandradev\.vscode\spaceshooter_ByJanaChumi\spaceshooter_ByJanaChumi\items\17.png"
            ),
            arcade.XYWH(self.x, self.y, 120, 120),
            angle=self.angle - 90
        )

    def draw_health_bar(self):
        bar_width = 200
        bar_height = 15
        health_percentage = self.health / self.max_health
        health_width = health_percentage * bar_width

        bar_x = self.x
        bar_y = self.y + self.radius + 40

        arcade.draw_rect_filled(
            arcade.XYWH(bar_x, bar_y, bar_width, bar_height), arcade.color.RED)
        
        if health_percentage > 0.7:
            health_color = arcade.color.GREEN
        elif health_percentage > 0.4:
            health_color = arcade.color.YELLOW
        else:
            health_color = arcade.color.RED

        arcade.draw_rect_filled(
            arcade.XYWH(bar_x - (bar_width - health_width) / 2, bar_y, health_width, bar_height), health_color)
        
        arcade.draw_rect_outline(
            arcade.XYWH(bar_x, bar_y, bar_width, bar_height), arcade.color.WHITE, 2)
        
        arcade.draw_text(f"BOSS HP: {self.health}/{self.max_health}",
                         bar_x - 80, bar_y + 25, arcade.color.WHITE, 12)
        
        def is_off_screen(self):
            return (self.x < -100 or self.x > SCREEN_WIDTH + 1 or
                    self.y < -100 or self.y > SCREEN_HEIGHT + 1)


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.radius = 4 * BULLET_SCALE
        self.texture = arcade.load_texture(
            r"C:\Users\Chandradev\.vscode\spaceshooter_ByJanaChumi\spaceshooter_ByJanaChumi\items\bullets\4.png"
        )

    def update(self):
        # Move bullet on based angle
        self.x += math.cos(math.radians(self.angle)) + self.speed
        self.y += math.sin(math.radians(self.angle)) + self.speed

    def draw(self):
        arcade.draw_texture_rect(
            self.texture,
            arcade.XYWH(self.x, self.y, 20, 20),
            angle=self.angle - 90
        )

    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)
                
class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.bg_texture = arcade.load_texture(
            r"C:\Users\Chandradev\.vscode\space_shooter_files\Space Shooter files\background\bg-preview-big.png"
        )
        self.player_texture = arcade.load_texture(
            r"C:\Users\Chandradev\.vscode\spaceshooter_ByJanaChumi\spaceshooter_ByJanaChumi\items\11.png"
        )

        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0
        self.player_radius = 150 * PLAYER_SCALE


        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.boss_bullets = []
        self.particles = []
        self.powerups = []
        self.boss = None
        self.enemy_spwan_timer = 0
        self.boss_spwan_timer = random.uniform(15, 20)
        self.shoot_cooldown = 0

        self.health = 100
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.paused = False
        self.shield_timer = 0
        self.sound_shoot = arcade.load_sound(
            r"C:\Users\Chandradev\.vscode\space_shooter_files\Space Shooter files\Sound FX\shot 1.wav"
        )
        self.sound_explosion = arcade.load_sound(
            r"C:\Users\Chandradev\.vscode\space_shooter_files\Space Shooter files\Sound FX\explosion.wav"
        )
        self.sound_hit = arcade.load_sound(
            r"C:\Users\Chandradev\.vscode\space_shooter_files\Space Shooter files\Sound FX\hit.wav"
        )
        self.bg_music = arcade.load_sound(
            r"C:\Users\Chandradev\.vscode\space_shooter_files\Space Shooter files\music\exports\space-asteroids.wav"
        )
        self.music_player = self.bg_music.play(loop=True)

        self.keys_pressed = set()
        self.score_text = arcade.Text(
            "Score: 0", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16
        )
        self.health_text = arcade.Text(
            "Health = 100", 10, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16
        )

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.bg_texture,
            arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        if not self.game_started:
            arcade.draw_text("GALAXY SHOOTER", SCREEN_WIDTH / 2 - 220, SCREEN_HEIGHT / 2 + 60,
                             arcade.color.CYAN, 48)
            arcade.draw_text("Press ENTER to Start", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                             arcade.color.WHITE, 24,)
            arcade.draw_text("WASD | Mouse Aim | CLICK/Space to Shoot",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50,
                             arcade.color.LIGHT_GRAY, 14)
            
            return
        
        if self.paused:
            arcade.draw_text("PAUSED", SCREEN_WIDTH / 2 - 80, SCREEN_HEIGHT / 2,
                             arcade.color.YELLOW, 48)
            arcade.draw_text("Press P to Resume", SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 60,
                             arcade.color.WHITE, 20)

        self.score_text.value = f"Score : {self.score}"
        self.health_text.value = f"Health : {self.health}"
        self.score_text.draw()
        self.health_text.draw()
        arcade.draw_texture_rect(
            self.player_texture,
            arcade.XYWH(self.player_x, self.player_y, 60, 60),
            angle=self.player_angle - 90
        )

        if self.shield_timer > 0:
            arcade.draw_circle_outline(
                self.player_x, self.player_y,
                self.player_radius + 10,
                arcade.color.CYAN, 3)
        
        if self.boss:
            self.boss.draw()
            self.boss.draw_health_bar()
        
        if self.boss and self.boss.y > SCREEN_HEIGHT:
            arcade.draw_text("BOSS INCOMING",
               SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
               arcade.color.RED, 36, anchor_x="center")

        if self.game_over:
            
            arcade.draw_text("GAME OVER",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40,
                arcade.color.RED, 36, anchor_x= "center"
            )
            arcade.draw_text(f"Score: {self.score}",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                arcade.color.WHITE, 24, anchor_x="center"
            )
            arcade.draw_text("Press R to Restart", 
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40,
                arcade.color.WHITE, 18, anchor_x="center"
            )

        for bullet in self.bullets:
            bullet.draw()

        for enemy in self.enemies:
            enemy.draw()
        
        if self.boss:
            self.boss.draw()
            self.boss.draw_health_bar()

        for powerup in self.powerups:
            powerup.draw()

        for particle in self.particles:
            particle.draw()
        
        for eb in self.enemy_bullets:
            if hasattr(eb, 'draw'):
                eb.draw()

        
    def on_update(self, delta_time):
        if self.game_over:
            return
        if not self.game_started or self.paused:
            return
        
        self.shoot_cooldown -= delta_time

        if self.shield_timer > 0:
            self.shield_timer -= delta_time 

        self.enemy_spwan_timer -= delta_time

        if self.boss is None:
            self.boss_spwan_timer -= delta_time
            if self.boss_spwan_timer <= 0:
                self.boss = Boss()

        for powerup in self.powerups[:]:
            distance = math.sqrt((powerup.x - self.player_x)**2
                        + (powerup.y - self.player_y)**2)
            if distance < powerup.radius + self.player_radius:
                if powerup.type == "heart":
                    self.health = min(100, self.health + 20)
                elif powerup.type == "shield":
                    self.shield_timer = 15
                elif powerup.type == "rapid_fire":
                    self.shoot_cooldown = 0.05
                self.powerups.remove(powerup)

        if random.randint(1, 500) == 1:
            self.powerups.append(Powerup(
                random.uniform(0, SCREEN_WIDTH),
                SCREEN_HEIGHT,
                random.choice(["rapid_fire", "shield", "heart"])
            ))

        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.y < 0:
                self.powerups.remove(powerup)

        if arcade.key.SPACE in self.keys_pressed:
            self.shoot()

        if self.boss:
            self.boss.update(self.player_x, self.player_y, delta_time)

        if self.enemy_spwan_timer <= 0:
            self.enemies.append(Enemy())
            self.enemy_spwan_timer = ENEMY_SPWAN_RATE
        if arcade.key.W in self.keys_pressed:
            self.player_y += PLAYER_SPEED
        if arcade.key.S in self.keys_pressed:
            self.player_y -= PLAYER_SPEED
        if arcade.key.A in self.keys_pressed:
            self.player_x -= PLAYER_SPEED
        if arcade.key.D in self.keys_pressed:
            self.player_x += PLAYER_SPEED

        self.player_x = max(self.player_radius, min(
            SCREEN_WIDTH - self.player_radius, self.player_x))
        self.player_y = max(self.player_radius, min(
            SCREEN_HEIGHT - self.player_radius, self.player_y))
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

        for enemy in self.enemies[:]:
            bullet = enemy.update(self.player_x, self.player_y, delta_time)
            if bullet is not None:
                if isinstance(bullet, EnemyBullet):
                    self.enemy_bullets.append(bullet)
                else:
                    print(type(bullet))

            distance = math.sqrt((enemy.x - self.player_x)**2    
                               + (enemy.y - self.player_y)**2)    
            
            if distance < enemy.radius + self.player_radius:
                if self.shield_timer <= 0:
                    self.health -= 10
                    arcade.play_sound(self.sound_hit)

                self.health = max(0, self.health)
                self.enemies.remove(enemy)
                if self.health <= 0:
                    self.game_over = True
                break

            elif enemy.is_of_screen():
                self.enemies.remove(enemy)
            for eb in self.enemy_bullets[:]:
                if isinstance(eb, EnemyBullet):
                    eb.update()
                    if eb.is_off_screen():
                        self.enemy_bullets.remove(eb)
                else:
                    self.enemy_bullets.remove(eb)


        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                distance = math.sqrt((bullet.x - enemy.x)
                                     ** 2 + (bullet.y - enemy.y)**2)
                if distance < bullet.radius + enemy.radius:
                    enemy.health -= 1
                    self.bullets.remove(bullet)
                    if enemy.health <= 0:
                        for _ in range(20):
                            self.particles.append(Particle(enemy.x, enemy.y))
                            arcade.play_sound(self.sound_explosion)
                        self.enemies.remove(enemy)
                        self.score += 10
                    break
        if self.boss:
            for bullet in self.bullets[:]:
                distance = math.sqrt((bullet.x - self.boss.x)**2
                            + (bullet.y - self.boss.y)**2)
                if distance < bullet.radius + self.boss.radius:
                    self.bullets.remove(bullet)
                    dead = self.boss.take_damage()
                    if dead:
                        self.score += 100
                        self.boss = None
                    break

        for eb in self.enemy_bullets[:]:
            distance = math.sqrt((eb.x - self.player_x)**2
                        + (eb.y - self.player_y)**2)
            if distance < eb.radius + self.player_radius:
                if self.shield_timer <= 0:
                    self.health -= 10
                    self.health = max(0, self.health)
                    if self.health <= 0:
                        self.game_over = True
                self.enemy_bullets.remove(eb)
                    

    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullet_x = self.player_x + \
                math.cos(math.radians(self.player_angle)) * self.player_radius
            bullet_y = self.player_y + \
                math.sin(math.radians(self.player_angle)) * self.player_radius
            self.bullets.append(Bullet(bullet_x, bullet_y, self.player_angle))
            arcade.play_sound(self.sound_shoot)
            self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN

    def on_key_press(self, symbol, modifiers):
        self.keys_pressed.add(symbol)

        if symbol == arcade.key.ENTER and not self.game_started:
            self.game_started = True
            
        elif symbol == arcade.key.P and self.game_started and not self.game_over:
            self.paused = not self.paused

        elif symbol == arcade.key.R and self.game_over:
            self.restart_game()

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys_pressed:
            self.keys_pressed.remove(symbol)

    def on_mouse_motion(self, x, y, dx, dy):
        dx = x - self.player_x
        dy = y - self.player_y 
        self.player_angle = math.degrees(math.atan2(dy, dx))
        
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.shoot()

    def restart_game(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0
        self.bullets.clear()
        self.enemies.clear()
        self.enemy_bullets.clear()
        self.score = 0
        self.health = 100
        self.game_over = False
        self.boss = None
        self.boss_spwan_timer = random.uniform(15, 20)
        self.particles.clear()
        self.powerups.clear()
        self.shield_timer = 0
        self.paused = False


def main():
    window = GameWindow()
    arcade.run()

if __name__ == "__main__":
    main()




import pygame as pg
import sys
import random
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ROSE = (255, 0, 127)
GREEN = (0, 255, 0)
YELLOW = (255,215,0)
PASTEL_PURPLE=(177,162,202)
DEEP_PURPLE=(87, 8, 97)
DISPLAY_WIDTH = 400
DISPLAY_HEIGHT = 600
#frames per second
FPS = 35
class Game:
    def __init__(self, screen):
        self.screen = screen

        self.clock = pg.time.Clock()
        self.game_over = False
        self.game_exit = False
        self.pause = False
        self.started = False

        self.score = 0
        self.enemy_num = 5
        self.count = 0

        self.all_sprites = pg.sprite.Group()
        self.player_sprite = pg.sprite.GroupSingle()
        self.enemy_sprites = pg.sprite.Group()
        self.bullet_sprites = pg.sprite.Group()
        self.coin_sprites = pg.sprite.Group()
        self.effective_enemy_sprites = pg.sprite.GroupSingle()

        self.player = Player()
        self.enemy = None
        self.big_enemy = None
       
        self.player_sprite.add(self.player)
        self.all_sprites.add(self.player)
        #metoda kojom stvaramo neprijatelje
        self.create_enemies(self.enemy_num)

    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE or event.type == pg.KEYDOWN and event.key == pg.K_q:
                return True
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.create_bullets()
            if event.type == pg.KEYDOWN and event.key == pg.K_p:
                self.pause = True
            if self.game_over and event.type == pg.KEYDOWN and event.key == pg.K_c:
                self.__init__(self.screen)

 #metoda kojom stvaramo neprijatelje
    def create_enemies(self, num):
        for i in range(num): #više od jednog neprijatelja
            self.enemy = Enemy()
            self.all_sprites.add(self.enemy)
            self.enemy_sprites.add(self.enemy)

#metoda kojom stvaramo metke
    def create_bullets(self):
        bullet = self.player.shoot()
        self.bullet_sprites.add(bullet)
        self.all_sprites.add(bullet)


    def display_frame(self):
        bg_image = pg.image.load('img/bg.jpg') #dodavanje pozadinske slike
        self.all_sprites.update()

        if self.game_over:
            self.game_over_function() #kraj igre
        
        elif self.pause:
            self.paused() #pauziranje igre

        elif not self.started:
            self.game_intro() #pocetni zaslon

        elif self.started:
            self.check_collision() #detekcija sudara metka i neprijatelja

            self.screen.blit(bg_image, (0,0))
            self.all_sprites.draw(self.screen)
            self.text_score(self.score)

            pg.display.update()

   
   #detekcija sudara
    def check_collision(self):

        # gledamo je li neprijatelj udario u igrača
        hits = pg.sprite.spritecollide(self.player, self.enemy_sprites, False)

        # gledamo je li metak pogodio neprijatelja
        shoots = pg.sprite.groupcollide(self.enemy_sprites, self.bullet_sprites, True, True)
        
        # gledamo je li igrač dohvatio zlatnik
        touch_coin = pg.sprite.spritecollide(self.player, self.coin_sprites, True)

        # gledamo je li igrač pogodio zlatnik
        shot_coin = pg.sprite.groupcollide(self.coin_sprites, self.bullet_sprites, True, True)

        # gledamo je li igrač pogodio velikog neprijatelja
        big_enemy_hit = pg.sprite.groupcollide(self.effective_enemy_sprites, self.bullet_sprites, False, True)

        #gledamo je li veliki neprijatelj udario u igrača
        big_enemy_player_collide = pg.sprite.spritecollide(self.player,self.effective_enemy_sprites,False)


        if hits and big_enemy_player_collide:
            self.started = False
            self.game_over = True
           
        if shoots:
            #treba stvoriti nove neprijatelje jer se pogođeni metkom brišu iz grupe sprite.group koja sadrži neprijatelje
            for shoot in shoots:
                self.score = self.update_score(self.score, shoot.points)
                self.make_coins()
                self.make_big_enemy()
                self.create_enemies(1)

        if touch_coin or shot_coin:
            self.score = self.update_score(self.score, 5)
            self.make_coins()

        if big_enemy_hit:
            for x in big_enemy_hit:
                self.count = self.count + 1
                if self.count > 9:
                    self.big_enemy.killsprite()
                    self.count = 0
                    #neprijatelj nosi 10 bodova
                    self.score = self.update_score(self.score, 10)
                    self.make_coins()

        #u slučaju da neprijatelj napusti okvir igre, igra prestaje
        for enemy1 in self.enemy_sprites:
            if enemy1.rect.top > DISPLAY_HEIGHT - enemy1.rect.height:
                self.started = False
                self.game_over = True

        #snažni neprijatelj napušta okvir igre
        for enemy2 in self.effective_enemy_sprites:
            if enemy2.rect.top > DISPLAY_HEIGHT - enemy2.rect.height:
                self.started = False
                self.game_over = True


    def game_intro(self):
        intro = True
        while intro:
            self.intro_screen_over = pg.time.get_ticks()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()

#provjera koju je tipku na tipkovnici igrač pritisnuo (q ili c)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_c:
                        intro = False
                        self.started = True

                    elif event.key == pg.K_q:
                        pg.quit()
                        quit()
 #karakteristike početnog zaslona igre
            self.screen.fill(DEEP_PURPLE)
            self.message_to_screen("SHOOTER GAME", PASTEL_PURPLE, -130, size="medium")
            self.message_to_screen("Press C to continue", WHITE, 10, size="small")
            self.message_to_screen("or press Q to quit", WHITE, 50, size="small")
            pg.display.update()


    def game_over_function(self):
        self.all_sprites.remove(self.enemy_sprites, self.bullet_sprites, self.player_sprite)
        clock = pg.time.Clock()

        count = 0
        colours = [ROSE, PASTEL_PURPLE]
        menu_ = True
        while menu_:
            for event in pg.event.get():
                if event.key == pg.K_q:
                    pg.quit()
                    quit()
                elif event.key == pg.K_c:
                    self.game_intro()
            self.screen.fill(DEEP_PURPLE)
            count += 1
            if count%2 == 0:
                sel_color = colours[0] #game over(rozo)
            else:
                sel_color = colours[1] #game over (ljubičasto)
                #karakteristike zaslona za kraj igre
            self.message_to_screen("GAME", sel_color, -130, size="medium")
            self.message_to_screen("OVER", sel_color, -50, size="medium")
            self.message_to_screen("Press C to start new game", WHITE, 10, size="small")
            self.message_to_screen("or press Q to quit", WHITE, 50, size="small")

            pg.display.update()
            clock.tick(6)
#metoda koja ažurira trenutno ostvareni rezultat
    def update_score(self, score, num):
        score = score + num
        return score
#metoda koja ispisuje ostvareni rezultat na ekran
    def text_score(self, score):
        smallfont = pg.font.SysFont("memphis", 30)
        text = smallfont.render("REZULTAT: " + str(score), True, PASTEL_PURPLE)
        self.screen.blit(text, [0,0])

    def paused(self):
        paused = True
        clock = pg.time.Clock()

#mogućnost nastavka igre pritiskom tipke c ili prekida igre pritiskom tipke q tijekom pauze 
        while paused:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_c:
                        paused = False
                        self.pause = False

                    elif event.key == pg.K_q:
                        pg.quit()
                        quit()

#karakteristike pauziranog zaslona
            self.screen.fill(PASTEL_PURPLE)
            self.message_to_screen("Paused", DEEP_PURPLE, -120, size="big")
            self.message_to_screen("Press C to continue",WHITE, -50, size="small")
            self.message_to_screen("or Q to quit", WHITE, 0, size="small")

            pg.display.update()
            clock.tick(6)

    def message_to_screen(self, msg, color, y_displace=0, size="small"):  
        textSurface, textRect = self.text_objects(msg, color, size)
        textRect.center = (DISPLAY_WIDTH / 2), (DISPLAY_HEIGHT / 2) + y_displace
        self.screen.blit(textSurface, textRect)

#definiranje fontova
    def text_objects(self, text, color, size):
        smallfont = pg.font.SysFont("rockwell", 25)  
        mediumfont = pg.font.SysFont("rockwell", 50)
        bigfont = pg.font.SysFont("rockwell", 65)

        if size == "small":
            textSurf = smallfont.render(text, True, color)
        elif size == "medium":
            textSurf = mediumfont.render(text, True, color)
        elif size == "big":
            textSurf = bigfont.render(text, True, color)

        return textSurf, textSurf.get_rect()


    def make_coins(self):
        if self.score % 10 == 0:
            self.coin = Coins()
            self.coin_sprites.add(self.coin)
            self.all_sprites.add(self.coin)


    def make_big_enemy(self):
        #ne može se pojaviti više od jednog snažnog neprijatelja
        if len(self.effective_enemy_sprites) == 0 and self.score % 10 == 0:
            self.big_enemy = Effective_enemy()
            self.effective_enemy_sprites.add(self.big_enemy)
            self.all_sprites.add(self.big_enemy)

#klasa Bullets
class Bullets(pg.sprite.Sprite):
    def __init__(self, position, move): # x,y jer se metak ispali uvijek s mjesta na kojem se nalazimo (igrač)
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((4, 10))
        self.image.fill(DEEP_PURPLE)
        self.rect = self.image.get_rect(center = position)
        self.speedy = move #metak ide od dna put vrha

    def update(self, *args):
        self.rect.y -= self.speedy

        #u slučaju da je metak promašio neprijatelja, metak se briše i ne nastavlja beskonačno putovati
        if self.rect.bottom < 0:
            self.kill()

#klasa Coins
class Coins(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load('img/coin2.png')
        self.rect = self.image.get_rect()
        self.speed = 10
        self.rect.x = random.randrange(0, DISPLAY_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-300, -10)

    def update(self, *args):
        self.rect.y += self.speed
        #ako zlatnik dode do dna, ostaje na dnu
        if self.rect.y >= DISPLAY_HEIGHT-self.rect.height-30 and self.speed >=0:
            self.speed = 0

#klasa Player
class Player(pg.sprite.Sprite):
    player_position = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT-50) # početna pozicija igrača
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load('img/player.png') #dodavanje slike neprijatelja
        self.rect = self.image.get_rect(center = self.player_position)
        self.move_x = 15
        self.move_bullet = 35
        self.bounds = pg.Rect(10, DISPLAY_HEIGHT-60, DISPLAY_WIDTH - 20, 25) #granice za igračevo napuštanje ekrana

    def update(self, *args):
        keys = pg.key.get_pressed()
        self.move_player(keys)

    def move_player(self,keys):
        if keys[pg.K_LEFT]:

            self.rect.move_ip(-self.move_x, 0)

        elif keys[pg.K_RIGHT]:

            self.rect.move_ip(self.move_x, 0)

        self.rect.clamp_ip(self.bounds)


    def shoot(self):
        return Bullets(self.rect.midtop, self.move_bullet)

#klasa Enemy
class Enemy(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image_names = ['img/asteroid0.png', 'img/asteroid1.png', 'img/asteroid2.png', 'img/asteroid3.png', 'img/asteroid4.png']
        self.random_img = random.choice(self.image_names)
        self.image = pg.image.load(self.random_img)


        self.rect = self.image.get_rect()

        self.rect.x = random.randrange(self.rect.width, DISPLAY_WIDTH - self.rect.width-10)
        self.rect.y = random.randrange(-300, -70)

        self.speed = random.randrange(2, 7) #brzina objekata je random broj generiran u ovom rasponu
        self.points = self.different_scores(self.random_img)

    def update(self, *args):
        self.rect.y += self.speed

#neprijatelji vrijede različiti broj bodova
    def different_scores(self, rand_img):
        if rand_img == 'img/asteroid0.png':
            return 6
        elif rand_img == 'img/asteroid1.png' or rand_img == 'img/asteroid2.png':
            return 5
        else:
            return 2

#klasa Effective_Enemy(snažni neprijatelj)
class Effective_enemy(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load('img/boss.png')
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(self.rect.width, DISPLAY_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-300, -self.rect.height)
        self.speed = 2

    def update(self, *args):
        self.rect.y += self.speed

    def killsprite(self):
        self.kill()

def main():
    pg.init()
    screen = pg.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT))
    pg.display.set_caption('Shooter game')
    icon = pg.image.load('img/player.png')
    pg.display.set_icon(icon)
    clock = pg.time.Clock()
    game = Game(screen)

    gameExit = False

    while not gameExit:
        gameExit = game.process_events()
        game.display_frame()
        clock.tick(FPS)
    pg.quit()

if __name__ == '__main__':
    main()
import pygame,sys
from player import Player
import obstacle
from alien import Alien, Extra  
from random import choice,randint
from laser import Laser

red = (241,79,80)

class Game:
    def __init__(self):
        #player setup
        player_sprite = Player((screen_width/2, screen_height),screen_width,5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        #health and score setup
        self.lives = 3
        self.live_surf = pygame.image.load("Graphics\player.png").convert_alpha()
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 3 + 20)
        self.score = 0
        self.font = pygame.font.Font("Graphics\Pixeled.ttf",20) #font size
        #get_size gets the coordinates of the player image we imported, and [0] splices the x-coordinate only 
        #so the width*2 for 2 lives, and makes up for a + 20 offset for spacing between lives

        #obstacle setup
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)] #creates x-positions for the different obstacles
        self.create_multiple_obstacles(*self.obstacle_x_positions,x_start = screen_width/15.25,y_start = 480) #last 3 numbers are the offset arugments represented by the parameter *offset

        #Alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows = 6, cols = 8)
        self.alien_direction = 1

        #Extra setup
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400,800)

        #Audio setup
        music = pygame.mixer.Sound("Audio\music.wav")
        music.set_volume(0.2)
        music.play(loops = -1) 
        #0 means music plays once no repeat, 1 means one repeat, -1 is infinite
        self.laser_sound = pygame.mixer.Sound("Audio\laser.wav")
        self.laser_sound.set_volume(0.5)
        self.explosion_sound = pygame.mixer.Sound("Audio\Explosion.wav")
        self.explosion_sound.set_volume(0.3)

    def create_obstacle(self,x_start,y_start,offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size,red,x,y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self,*offset,x_start,y_start,): #tuple creating parameter allowing you to add how ever many arugments you want later
        for offset_x in offset: #each thing in the offset tuple parameter
            self.create_obstacle(x_start,y_start,offset_x) #offset_x here is the spacing between obstacles

    def alien_setup(self,rows,cols,x_distance = 60,y_distance = 48, x_offset = 70, y_offset = 100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0:
                    alien_sprite = Alien("yellow",x,y)
                elif 1 <= row_index <= 2:
                    alien_sprite = Alien("green",x,y)
                else:
                    alien_sprite = Alien("red",x,y)
                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_move_down(2)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(2)

    def alien_move_down(self,distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center,6,screen_height)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(["right","left"]),screen_width))
            self.extra_spawn_time = randint(400,800) #reset the time taken for it to spawn again i.e. repeat the cycle

    def collision_checks(self):

        #player collisions
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                #obstacle collisions
                if pygame.sprite.spritecollide(laser,self.blocks,True):
                    laser.kill()
                #meaning: for each laser in the for loop of player.sprite.lasers, if it hits the 
                #self.blocks (block variable), and 'True' then... BTW 'True' is the parameter for
                #the kill part of this in-built collide function

                #alien collisions
                aliens_hit = pygame.sprite.spritecollide(laser,self.aliens,True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()

                #extra collisions
                if pygame.sprite.spritecollide(laser,self.extra,True):
                    laser.kill()
                    self.score += 500

        #alien collisions
        if self.alien_lasers:
            for laser in self.alien_lasers:
                #obstacle collisions
                if pygame.sprite.spritecollide(laser,self.blocks,True):
                    laser.kill()
                
                #player collisions
                if pygame.sprite.spritecollide(laser,self.player,False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()

        #aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien,self.blocks,True)

                if pygame.sprite.spritecollide(alien,self.player,False):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        for live in range(self.lives):
            x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf,(x,8))

    def display_score(self):
        score_surf = self.font.render(f"score: {self.score}",False,"white") #f-string is concatenation basically with {}
        #false for anti-aliasing as pixel game
        #retro feel wanted, no smoothing out
        score_rect = score_surf.get_rect(topleft = (10,-10)) 
        #topleft most corner = (0,0) on the map and 'topleft' is specifying 
        #top left of the object should be (0,0)
        screen.blit(score_surf,score_rect)
    
    def victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render("You Won!",False,"white")
            victory_rect = victory_surf.get_rect(center = (screen_width / 2,screen_height / 2))
            screen.blit(victory_surf,victory_rect)

    def run(self):
        self.player.update()
        self.alien_lasers.update()
        self.extra.update()

        self.aliens.update(self.alien_direction)
        self.alien_position_checker()
        self.extra_alien_timer()
        self.collision_checks()
        
        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.display_lives()
        self.display_score()
        self.victory_message()
        #update all sprite groups
        #draw all sprite groups

class CRT:
    def __init__(self):
        self.kv = pygame.image.load("Graphics\kv.png").convert_alpha()
        self.kv = pygame.transform.scale(self.kv,(screen_width,screen_height)) #last 2 are the ratio references
    
    def create_crt_lines(self):
        line_height = 3
        line_amount = int(screen_height / line_height)
        for line in range(line_amount):
            y_pos = line * line_height
            pygame.draw.line(self.kv,"black",(0,y_pos),(screen_width,y_pos),1) 
            #drawing on the tv image, not on the screen, colour, start, end of line, width
            #not using self.xyz.draw() as we are needing to specify many things custom

    def draw(self):
        self.kv.set_alpha(randint(50,90)) #opacity function
        screen.blit(self.kv,(0,0))
        self.create_crt_lines()

if __name__ == "__main__":
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height)) #created a screen
    pygame.display.set_caption("Space Invaders by Amri") #created a caption for the screen
    clock = pygame.time.Clock() #creates function to limit fps

    game = Game()
    crt = CRT()

    ALIENLASER = pygame.USEREVENT + 1 #caps means constant, pygame.USEREVENT: This is a constant provided by Pygame that marks the starting point for user-defined events. 
                                      #Pygame reserves a block of event IDs starting from pygame.USEREVENT that developers can use to create their own custom events, ensuring
                                      #they don't conflict with Pygame's built-in events and the +1 means by adding 1 to pygame.USEREVENT, you create a unique identifier for a specific custom event

    pygame.time.set_timer(ALIENLASER,800) #pygame.time.set_timer(): This function is used to create a timer that repeatedly generates a specific event at a set interval. When the interval elapses,
                                          #the specified event is automatically posted to Pygame's event queue.
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()

        screen.fill((30,30,30)) #drawing the background colour
        game.run()
        crt.draw() #must reference the method in its class, not from another class

        pygame.display.flip() #drawing anything that was drawn in the game loop
        clock.tick(60) #limits frame rate to 60fps
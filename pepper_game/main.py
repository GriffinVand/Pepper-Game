import pygame as pg
import game as gm
import sys
import time
import asyncio

async def main():
    ###
    #initialize pygame and theme music
    pg.init()
    GLOBAL_VOLUME = 1
    game_theme = pg.mixer.Sound('Sounds/GriffinTheme.ogg')
    end_theme = pg.mixer.Sound('Sounds/GriffinTheme2.ogg')
    game_theme.set_volume(0.3 * GLOBAL_VOLUME)
    end_theme.set_volume(0 * GLOBAL_VOLUME)
    game_theme.play(loops=-1)
    end_theme.play(loops=-1)
    ###
    ###
    #window initialization
    width = 800
    height = 600
    window = pg.display.set_mode((width,height))
    ###
    ###
    #create opening screen ui
    default_font = pg.font.SysFont('Comic Sans MS', 32)
    buy_pepper_button = pg.Rect(0, 0, 300, 50)
    buy_pepper_text = default_font.render('buy the pepper', True, (255, 255, 255))
    buy_pepper_button.center = (width // 2, height // 2)
    buy_pepper_text_rect = buy_pepper_text.get_rect(center = buy_pepper_button.center)

    background_image = pg.image.load('Sprites/GriffinBackground.png')
    background_image = pg.transform.scale(background_image, (width, height))
    pepper_image = pg.image.load('Sprites/ThePepper.png')
    pepper_image = pg.transform.scale(pepper_image, (100, 100))
    griffin_image = pg.image.load('Sprites/Griffin.png')
    griffin_image = pg.transform.scale(griffin_image, (100, 100))
    griffin_image_rect = pg.Rect(0, 0, 100, 100)
    griffin_image_rect.center = (width // 2 + 100, 200)
    pepper_image_rect = pg.Rect(0, 0, 100, 100)
    pepper_image_rect.center = (width // 2, 200)
    pepper_rotation = 0

    opening = True
    ###
    ### opening screen loop
    ###
    while opening:
        window.fill((255, 0, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if buy_pepper_button.collidepoint(event.pos):
                    click_sound = pg.mixer.Sound('Sounds/GriffinCaptured.ogg')
                    click_sound.set_volume(0.4 * GLOBAL_VOLUME)
                    click_sound.play()
                    opening = False
        
        window.blit(background_image, (0, 0))

        mouse_position = pg.mouse.get_pos()
        if buy_pepper_button.collidepoint(mouse_position):
            pg.draw.rect(window, (0, 255, 0), buy_pepper_button)
            griffin_image = pg.image.load('Sprites/GriffinFire1.png')
            griffin_image = pg.transform.scale(griffin_image, (100, 100))
        else:
            pg.draw.rect(window, (0, 0, 255), buy_pepper_button)
            griffin_image = pg.image.load('Sprites/Griffin.png')
            griffin_image = pg.transform.scale(griffin_image, (100, 100))
        
        window.blit(buy_pepper_text, buy_pepper_text_rect)
        pepper_rotation += 0.1
        rotated_pepper = pg.transform.rotate(pepper_image, pepper_rotation)
        rotated_rect = rotated_pepper.get_rect(center=pepper_image_rect.center)
        window.blit(rotated_pepper, rotated_rect)
        window.blit(griffin_image, griffin_image_rect)

        pg.display.flip()
        await asyncio.sleep(0)

    ###
    ### start button pressed
    ###
    # go to black and wait 3 seconds
    loading_image = pg.image.load('Sprites/LoadingScreen.jpg')
    loading_image = pg.transform.scale(loading_image, (width, height))
    window.fill((0, 0, 0))
    window.blit(loading_image, (0, 0))
    pg.display.flip()
    game_theme.set_volume(0 * GLOBAL_VOLUME)
    await asyncio.sleep(5)
    game_theme.set_volume(0.3 * GLOBAL_VOLUME)

    ###
    ###
    #Ammo UI
    default_text = default_font.render('Ammo Text', True, (255, 255, 255))
    default_text_bg = pg.image.load('Sprites/Hello.jpg')
    default_text_bg_rect = pg.Rect(0, 0, 250, 50)
    default_text_bg = pg.transform.scale(default_text_bg, (default_text_bg_rect.width, default_text_bg_rect.height))
    default_text_rect = default_text.get_rect(center = (default_text_bg_rect.center))
    ###
    ###
    #Health UI
    health_text = default_font.render('Health Text', True, (255, 0, 0))
    health_text_bg = pg.image.load('Sprites/Hiya.jpg')
    health_text_bg_rect = pg.Rect(width-250, 0, 250, 50)
    health_text_bg = pg.transform.scale(health_text_bg, (health_text_bg_rect.width, health_text_bg_rect.height))
    health_text_rect = default_text.get_rect(center=(health_text_bg_rect.center))
    ###
    ###
    #Difficulty UI
    difficulty_text = default_font.render('Difficulty Text', True, (0, 255, 0))
    difficulty_text_bg = pg.image.load('Sprites/Difficulty.jpg')
    difficulty_text_bg_rect = pg.Rect(width // 2, 0, 200, 50)
    difficulty_text_bg_rect.center = (width // 2, 25)
    difficulty_text_bg = pg.transform.scale(difficulty_text_bg, (difficulty_text_bg_rect.width, difficulty_text_bg_rect.height))
    diff_text_rect = difficulty_text.get_rect(center=(width // 2, 50))
    ###
    ###
    #Background image
    bg_size = 50
    bg = pg.image.load('Sprites/BellPepper.png')
    bg_scaled = pg.transform.scale(bg, (50, 50))
    bg_rect = pg.Rect(0, 0, 50, 50)
    ###
    ###
    #Delta_time prereqs
    fps = 30
    elapsed_time = 0
    running = True
    previous = pg.time.get_ticks()
    ###
    ###
    #Create a game instance and add necessary objects
    Game1 = gm.game(GLOBAL_VOLUME)
    GameMode = gm.game_mode(Game1, window, 'GameMode')
    Game1.gamemode = GameMode
    Player = gm.player_object(Game1, window, 'Player', (350, 250), (100, 100), 'Sprites/GriffinLaugh1.png')
    GoblinSpawner = gm.Goblin_Spawner(Game1, window, 'GoblinSpawner', gm.goblin_object)
    SoulSpawner = gm.Soul_Spawner(Game1, window, 'SoulSpawner', gm.soul_object)
    PepperMan = gm.pepper_man(Game1, window, 'PepperMan')
    Game1.add_game_objects([Player, GoblinSpawner, SoulSpawner, PepperMan])
    ###
    ### Main Game Loop
    ###
    while Game1.running:
        current = pg.time.get_ticks()
        delta_time = (current - previous) / 1000
        elapsed_time += delta_time
        previous = current
        
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    button = event.button
                    if button == 1:
                        Player.check_for_hits()
                
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        Player.fire_projectile()
                
        
        window.fill((0, 0, 0))
        default_text = default_font.render(f'ammo {Player.ammo}', True, (255, 255, 255))
        health_text = default_font.render(f'{Player.health} health', True, (255, 0, 0))
        difficulty_text = default_font.render(f'{Game1.gamemode.difficulty}', True, (0, 255, 0))
        health_text_rect = default_text.get_rect(center=(health_text_bg_rect.center))
        default_text_rect = default_text.get_rect(center = (default_text_bg_rect.center))
        diff_text_rect = difficulty_text.get_rect(center=(width // 2, 25))
        for x in range(width//bg_size):
            for y in range(height//bg_size):
                bg_rect = pg.Rect(50*x, 50*y, bg_size, bg_size)
                window.blit(bg_scaled, bg_rect)

        window.blit(default_text_bg, default_text_bg_rect)
        window.blit(default_text, default_text_rect)
        window.blit(health_text_bg, health_text_bg_rect)
        window.blit(health_text, health_text_rect)
        

        
        
        Game1.update_game(delta_time)
        window.blit(difficulty_text_bg, difficulty_text_bg_rect)
        window.blit(difficulty_text, diff_text_rect)
        pg.display.flip()
        await asyncio.sleep(0)

    ###
    ### Player Lost
    ###
    #End screen
    final_score = Game1.gamemode.difficulty
    game_theme.set_volume(0)
    the_end_sound = pg.mixer.Sound('Sounds/TheEnd.ogg')
    the_end_sound.set_volume(2 * GLOBAL_VOLUME)
    the_end_sound.play(loops=-1)
    window.fill((0, 0, 0))
    pg.display.flip()
    await asyncio.sleep(2)
    end_theme.set_volume(0.5 * GLOBAL_VOLUME)


    large_font = pg.font.SysFont('Comic Sans MS', 100)
    large_font2 = pg.font.SysFont('Comic Sans MS', 110)
    you_lost = large_font.render(f'{final_score}', True, (0, 255, 0))
    you_lost2 = large_font2.render(f'{final_score}', True, (0, 0, 0))
    you_lost_rect = you_lost.get_rect(center = (width // 2, height // 2))
    bg_end = pg.image.load('Sprites/BellPepper2.png')
    bg_full = pg.transform.scale(bg_end, (width, height))
    ###
    ###
    #Loops until player manually exits
    while True:
        window.fill((0, 0, 0))
        window.blit(bg_full, (0, 0))
        window.blit(you_lost2, you_lost_rect)
        window.blit(you_lost, you_lost_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

        pg.display.flip()

        await asyncio.sleep(0)

asyncio.run(main())



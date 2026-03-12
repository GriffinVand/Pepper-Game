import pygame as pg
import game_math as gmath
import math
import random as rd

def Load_Texture(file):
    texture = pg.image.load(file)
    return texture

def Draw_Sprite(surface, texture, location, size):
    scaled_texture = pg.transform.scale(texture, (size[0], size[1]))
    scaled_rect = pg.Rect(location[0], location[1], size[0], size[1])
    surface.blit(scaled_texture, scaled_rect)

def Play_Animation(files):
    textures = []
    for file in files:
        textures.append(Load_Texture(file))
    if len(textures) > 0:
            next_texture = textures.pop(0)
    return next_texture, textures

#game class
#maintains a list of all game objects and can update them and their components
class game:
    def __init__(self, globalvolume):
        self.game_objects: list[game_object] = []
        self.player_object = None  
        self.running = True
        self.globalvolume = globalvolume
        self.gamemode: game_mode = None

    #called by game loop
    def update_game(self, delta_time):
        self.update_game_objects(delta_time)
        self.gamemode.Update(delta_time)

    #adding any amount of game objects to game object list
    def add_game_objects(self, game_objects):
        for game_object in game_objects:
            self.game_objects.append(game_object)
            if game_object.name == 'Player':
                self.player_object = game_object
                print('Got player')

    #update each game object in game object list
    def update_game_objects(self, delta_time):
        for game_object in self.game_objects:
            game_object.Static_Update(delta_time, self)

    #remove a game object
    def remove_game_object(self, game_object_to_remove):
        if game_object_to_remove in self.game_objects:
            print('Removed game object')
            self.game_objects.remove(game_object_to_remove)
        else:
            print('Did not find game object')

    def find_objects_of_type(self, type):
        found_instances = []
        for object in self.game_objects:
            if object.name == type:
                found_instances.append(object)
        return found_instances

class game_mode:
    def __init__(self, world:game, window, name):
        self.world = world
        self.window = window
        self.name = name
        self.difficulty = 1
        self.score = 0
        self.elapsed_time = 0
    
    def Update(self, delta_time):
        self.elapsed_time += delta_time
        if self.elapsed_time >= 10:
            self.elapsed_time = 0
            self.difficulty += 1

class game_object:
    def __init__(self, world: game, window, name):
        self.world: game = world
        self.window = window
        self.name = name
        self.components = []

    #ddds component if it doesn't already exist
    def add_component(self, component):
        if self.has_component(type(component)):
            return
        self.components.append(component)

    #returns if component exists
    def has_component(self, component_class: type):
        return any(isinstance(component, component_class) for component in self.components)
    
    #returns component if it exists
    def get_component(self, component_class: type):
        if self.has_component(component_class):
            for component in self.components:
                if isinstance(component, component_class):
                    return component
                
    #not overriden by children
    def Static_Update(self, delta_time:float, world:game):
        self.Update_Components(delta_time, world)
        self.Update(delta_time, world)

    #self explanatory
    def Update_Components(self, delta_time:float, world:game):
        for component in self.components:
            component.Update(delta_time, world)

    #repeating logic contained here
    def Update(self, delta_time:float, world:game):
        pass

    #called by collision component if collision is detected
    def on_collision_enter(self, other_object):
        pass
    
    #handles damage done to this object
    def apply_damage(self, damage):
        pass

class player_object(game_object):

    def __init__(self, world, window, name, location, scale, texture_file):
        super().__init__(world, window, name)
        self.texture = Load_Texture(texture_file)
        self.health = 10
        transform_comp = transform_component(self, location, scale, 0)
        render_comp = render_component(self, window, texture_file, transform_comp, 500)
        render_comp.add_animation('default', ['Sprites/GriffinLaugh1.png', 'Sprites/GriffinLaugh3.png',])
        render_comp.add_animation('shoot', ['Sprites/GriffinFire1.png', 'Sprites/GriffinFire2.png'])
        render_comp.add_animation('hurt', ['Sprites/GriffinHurt1.png', 'Sprites/GriffinHurt2.png'])
        collider_comp = box_collider_component(self, transform_comp, True)
        self.components = [transform_comp, render_comp, collider_comp]
        self.ammo = 50
        self.fire_cooldown = 0
        self.fire_rate = 0.1
        self.hurt_sounds = [pg.mixer.Sound('Sounds/GriffinHurt2.ogg'),
                            pg.mixer.Sound('Sounds/GriffinHurt3.ogg'),]
        self.fire_sound = pg.mixer.Sound('Sounds/PopSound.ogg')

    #handles damage done to this object
    def apply_damage(self, damage):
        hurt_sound = self.hurt_sounds[rd.randrange(0, len(self.hurt_sounds))]
        hurt_sound.set_volume(0.3 * self.world.globalvolume)
        hurt_sound.play()
        self.health -= 1
        if self.health <= 0:
            self.world.running = False
        render_comp: render_component = self.get_component(render_component)
        if render_comp:
            render_comp.play_animation('hurt', False)

    def Update(self, delta_time, world):
        self.fire_cooldown += delta_time

    #spawns a projectile object in direction of mouse
    def fire_projectile(self):
        if self.fire_cooldown >= self.fire_rate and self.ammo > 0:
            self.fire_cooldown = 0
            self.ammo -= 1
            transform_comp: transform_component = self.get_component(transform_component)
            if transform_comp:
                mouse_position = pg.mouse.get_pos()
                player_location = transform_comp.location
                player_scale = transform_comp.scale
                spawn_location = (player_location[0] + player_scale[0] // 2, player_location[1] + player_scale[1] // 2)
                direction = (mouse_position[0] - spawn_location[0], mouse_position[1] - spawn_location[1])
                direction = gmath.normalize(direction)
                new_projectile = projectile(self.world, self.window, 'bullet', spawn_location, (40, 40), 'Sprites/Skull/tile000.png', direction, 250)
                self.world.add_game_objects([new_projectile])
                self.fire_sound.set_volume(self.world.globalvolume)
                self.fire_sound.play()
                render_comp: render_component = self.get_component(render_component)
                if render_comp:
                    render_comp.play_animation('shoot', False)
        
    def check_for_hits(self):
        for object in self.world.game_objects:
            if object.name == 'pickup':
                mouse_position = pg.mouse.get_pos()
                object_transform = object.get_component(transform_component)
                if gmath.is_colliding_mouse(mouse_position, object_transform.location, object_transform.scale):
                    print('Hit pickup')
                    object.player_hit(self)



#goblin object that moves towards the player and damages the player if it gets close
class goblin_object(game_object):
    
    def __init__(self, world, window, name, location, scale, texture_file, speed):
        super().__init__(world, window, name)
        self.texture = Load_Texture(texture_file)
        transform_comp = transform_component(self, location, scale, 0)
        render_comp: render_component = render_component(self, window, texture_file, transform_comp, 250)
        render_comp.add_animation('default', ['Sprites/Enemy/EnemyIdle1.png',
                                              'Sprites/Enemy/EnemyIdle2.png',
                                              'Sprites/Enemy/EnemyIdle3.png'])
        collider_comp = box_collider_component(self, transform_comp, False)
        self.components = [transform_comp, render_comp, collider_comp]
        self.speed = speed
        self.health = 2
        self.death_sound = pg.mixer.Sound('Sounds/EnemyDeathSound.ogg')
        self.death_sound2 = pg.mixer.Sound('Sounds/GriffinHurtSound.ogg')
        self.hurt_sound = pg.mixer.Sound('Sounds/EnemyHurtSound.ogg')

    #if collision with player, hurt player
    def on_collision_enter(self, other_object:game_object):
        if other_object.name == 'Player':
            print('Hit Player')
            other_object.apply_damage(1)
            self.world.remove_game_object(self)

    #tries to find the player
    def Find_Player(self):
        player:player_object = self.world.player_object
        if player == None:
            return False
        elif player.has_component(transform_component):
            return True
        return False

    #move towards player
    def Update(self, delta_time:float, world:game):
        if self.Find_Player():
            player: player_object = self.world.player_object
            if player and player.has_component(transform_component):
                player_transform_comp: transform_component = player.get_component(transform_component)
                player_position = player_transform_comp.location
                transform_comp: transform_component = self.components[0]
                transform_comp.location = gmath.move_towards_location(transform_comp.location, player_position, 5, delta_time, self.speed)
    
    #handles damage done to this object
    def apply_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            if rd.randrange(0, 12) == 0:
                self.death_sound.set_volume(self.world.globalvolume)
                self.death_sound.play()
            else:
                self.hurt_sound.set_volume(self.world.globalvolume)
                self.hurt_sound.play()
            if rd.randrange(0, 2) == 0 and len(self.world.find_objects_of_type('pickup')) < 5:
                ammo_pickup = pickup(self.world, self.window, 'pickup', self.get_component(transform_component).location, (30, 30), 'Sprites/Garbage.png')
                self.world.add_game_objects([ammo_pickup])
            self.world.remove_game_object(self)
        else:
            self.hurt_sound.set_volume(self.world.globalvolume)
            self.hurt_sound.play()

#soul object that moves towards the player and damages the player if it gets close
class soul_object(game_object):
    
    def __init__(self, world, window, name, location, scale, texture_file, speed):
        super().__init__(world, window, name)
        self.texture = Load_Texture(texture_file)
        transform_comp = transform_component(self, location, scale, 0)
        render_comp: render_component = render_component(self, window, texture_file, transform_comp, 250)
        render_comp.add_animation('default', ['Sprites/Enemy/Soul1.png',
                                              'Sprites/Enemy/Soul2.png',
                                              'Sprites/Enemy/Soul3.png',
                                              'Sprites/Enemy/Soul4.png'])
        collider_comp = box_collider_component(self, transform_comp, True)
        self.components = [transform_comp, render_comp, collider_comp]
        self.speed = speed
        self.health = 1
        self.death_sound = pg.mixer.Sound('Sounds/EnemyDeathSound.ogg')
        self.hurt_sound = pg.mixer.Sound('Sounds/EnemyHurtSound.ogg')

    #same as goblin
    def on_collision_enter(self, other_object:game_object):
        if other_object.name == 'Player':
            print('Hit Player')
            other_object.apply_damage(3)
            self.world.remove_game_object(self)

    #same as goblin
    def Find_Player(self):
        player:player_object = self.world.player_object
        if player == None:
            return False
        elif player.has_component(transform_component):
            return True
        return False
    
    #same as goblin
    def Update(self, delta_time:float, world:game):
        if self.Find_Player():
            player: player_object = self.world.player_object
            if player and player.has_component(transform_component):
                player_transform_comp: transform_component = player.get_component(transform_component)
                player_position = player_transform_comp.location
                transform_comp: transform_component = self.components[0]
                transform_comp.location = gmath.move_towards_location(transform_comp.location, player_position, 5, delta_time, self.speed)
                if transform_comp.location[0] < player_position[0]:
                    render_comp: render_component = self.get_component(render_component)
                    render_comp.flipped_x = True
    #same as goblin
    def apply_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            if rd.randrange(0, 6) == 0:
                self.death_sound.set_volume(self.world.globalvolume)
                self.death_sound.play()
            else:
                self.hurt_sound.set_volume(self.world.globalvolume)
                self.hurt_sound.play()
            if rd.randrange(0, 2) == 0 and len(self.world.find_objects_of_type('pickup')) < 5:
                ammo_pickup = pickup(self.world, self.window, 'pickup', self.get_component(transform_component).location, (30, 30), 'Sprites/Garbage.png')
                self.world.add_game_objects([ammo_pickup])
            self.world.remove_game_object(self)
        else:
            self.hurt_sound.set_volume(self.world.globalvolume)
            self.hurt_sound.play()

#projectile is spawned with a direction and speed and simply moves in that direction until it collides with something
class projectile(game_object):
    def __init__(self, world, window:pg.surface, name, location, scale, texture_file, direction, speed):
        super().__init__(world, window, name)
        transform_comp = transform_component(self, location, scale, 0)
        render_comp = render_component(self, window, texture_file, transform_comp, 50)
        render_comp.add_animation('default', ['Sprites/Skull/tile000.png',
                                             'Sprites/Skull/tile001.png',
                                             'Sprites/Skull/tile002.png',
                                             'Sprites/Skull/tile004.png',
                                             'Sprites/Skull/tile005.png',
                                             'Sprites/Skull/tile006.png',
                                             'Sprites/Skull/tile008.png',
                                             'Sprites/Skull/tile009.png',
                                             'Sprites/Skull/tile010.png',
                                             'Sprites/Skull/tile012.png',
                                             'Sprites/Skull/tile013.png',
                                             'Sprites/Skull/tile014.png'])
        collider_comp = box_collider_component(self, transform_comp, True)
        self.components = [transform_comp, render_comp, collider_comp]
        self.direction = direction
        self.speed = speed

    def Update(self, delta_time:float, world:game):
        transform_comp: transform_component = self.get_component(transform_component)
        if transform_comp:
            transform_comp.location = gmath.move_in_direction(transform_comp.location, self.direction, delta_time, self.speed)
            if transform_comp.location[0] + transform_comp.scale[0] < 0 or transform_comp.location[0] > self.window.get_width() or transform_comp.location[1]+transform_comp.scale[1] < 0 or transform_comp.location[1] > self.window.get_height():
                self.world.remove_game_object(self)

    def on_collision_enter(self, other_object):
        if other_object.name == 'Goblin':
            other_transform: transform_component = other_object.get_component(transform_component)
            blood_effect = blood_splatter(self.world, self.window, 'blood', other_transform.location, (50, 50), 'Sprites/Blood1.png')
            self.world.add_game_objects([blood_effect])
            other_object.apply_damage(1)
            self.world.remove_game_object(self)

class pickup(game_object):
    def __init__(self, world, window:pg.surface, name, location, scale, texture_file):
        super().__init__(world, window, name)
        transform_comp = transform_component(self, location, scale, 0)
        render_comp = render_component(self, window, texture_file, transform_comp, 500)
        render_comp.add_animation('default', ['Sprites/Garbage.png', 'Sprites/Garbage2.png'])
        self.components = [transform_comp, render_comp]   

    def player_hit(self, player: player_object):
        player.ammo += rd.randrange(1, 6)
        pickup_sound = pg.mixer.Sound('Sounds/GarbageSound.ogg')
        pickup_sound.set_volume(self.world.globalvolume)
        pickup_sound.play()
        self.world.remove_game_object(self)

#spawns goblin objects over time
class Goblin_Spawner(game_object):
    def __init__(self, world: game, window: pg.Surface, name, object_class):
        super().__init__(world, window, name)
        self.object_class = object_class
        self.elapsed_time = 0
        self.spawn_time = 4 - (self.world.gamemode.difficulty * 0.3)
    
    def spawn_object(self, world:game):
        radius = 300
        center = (self.window.get_width() // 2, self.window.get_height() // 2)
        degree = rd.randrange(0, 360)
        angle = math.radians(degree)
        spawn_location = ((math.cos(angle) * radius) + center[0], (math.sin(angle) * radius) + center[1])
        new_goblin = goblin_object(self.world, self.window, 'Goblin', spawn_location, (50, 50), 'Sprites/Enemy/EnemyIdle1.png', 30)
        world.add_game_objects([new_goblin])

    def Update(self, delta_time:float, world:game):
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.spawn_time:
            self.spawn_time = 4 - (self.world.gamemode.difficulty * 0.3)
            self.elapsed_time = 0
            self.spawn_object(world)

#spawns soul objects over time
class Soul_Spawner(game_object):
    def __init__(self, world, window: pg.Surface, name, object_class):
        super().__init__(world, window, name)
        self.object_class = object_class
        self.elapsed_time = 0
        self.spawn_time = 6 - (self.world.gamemode.difficulty * 0.3)
    
    def spawn_object(self, world:game):
        radius = 300
        center = (self.window.get_width() // 2, self.window.get_height() // 2)
        degree = rd.randrange(0, 360)
        angle = math.radians(degree)
        spawn_location = ((math.cos(angle) * radius) + center[0], (math.sin(angle) * radius) + center[1])
        new_soul = soul_object(self.world, self.window, 'Goblin', spawn_location, (50, 50), 'Sprites/Enemy/Soul1.png', 80)
        world.add_game_objects([new_soul])

    def Update(self, delta_time:float, world:game):
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.spawn_time and self.world.gamemode.difficulty >= 3:
            self.elapsed_time = 0
            self.spawn_object(world)

#exists as a blood effect when enemies are hit
#just plays a single animations then deletes itself
class blood_splatter(game_object):
    def __init__(self, world, window, name, location, scale, texture_file):
        super().__init__(world, window, name)
        self.texture = pg.image.load(texture_file)
        transform_comp = transform_component(self, location, scale, 0)
        render_comp = render_component(self, self.window, texture_file, transform_comp, 50)
        render_comp.add_animation('default', ['Sprites/Blood1.png', 'Sprites/Blood2.png'])
        self.components = [transform_comp, render_comp]
        self.elapsed_time = 0

    def Update(self, delta_time, world):
        self.elapsed_time += delta_time * 1000
        if self.elapsed_time >= 100:
            self.world.remove_game_object(self)

#invisible object that just plays voicelines in game
class pepper_man(game_object):
    def __init__(self, world, window, name):
        super().__init__(world, window, name)
        self.voice_lines = [pg.mixer.Sound('Sounds/PepperMan1.ogg'),
                            pg.mixer.Sound('Sounds/PepperMan2.ogg'),
                            pg.mixer.Sound('Sounds/PepperMan3.ogg'),
                            pg.mixer.Sound('Sounds/PepperMan4.ogg')]
        self.elapsed_time = 0
        self.voice_line_timer = 5
        self.voice_line_min = 10
        self.voice_line_max = 20
    
    def Update(self, delta_time, world):
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.voice_line_timer:
            self.elapsed_time = 0
            self.voice_line_timer = rd.randrange(self.voice_line_min, self.voice_line_max)
            voice_line = self.voice_lines[rd.randrange(0, len(self.voice_lines))]
            voice_line.set_volume(self.world.globalvolume)
            voice_line.play()
###
###
###

#container component class
class component:
    def __init__(self, owner:game_object):
        self.owner = owner
    
    def Update(self, delta_time, world:game):
        pass

#transform component
#maintains location, scale, and rotation information for a game object
class transform_component(component):
    def __init__(self, owner, location: tuple[float, float], scale: tuple[float, float], rotation:float):
        super().__init__(owner)
        self.location = location
        self.scale = scale
        self.rotation = rotation

#box collider
#detects collision with other game objects with a box collider and can resolve that collision
class box_collider_component(component):
    def __init__(self, owner, transform:transform_component, static:bool):
        super().__init__(owner)
        self.transform = transform
        self.static = static
        self.colliding = False

    #check for collision each update
    def Update(self, delta_time:float, world:game):
            for object in world.game_objects:
                if object != self.owner and object.has_component(box_collider_component):
                        other_transform: transform_component = object.get_component(transform_component)
                        owner_transform = self.owner.get_component(transform_component)
                        if other_transform and owner_transform:
                            if gmath.is_colliding(owner_transform.location, owner_transform.scale, other_transform.location, other_transform.scale):
                                self.owner.on_collision_enter(object)
                                if not self.static:
                                    self.try_resolve_collision(owner_transform, other_transform)                            
    
    #uses the gmath resolve collision function to move this game object out of collision with another game object
    def try_resolve_collision(self, owner_transform:transform_component, other_transform:transform_component):
        while gmath.is_colliding(owner_transform.location, owner_transform.scale, other_transform.location, other_transform.scale):
            owner_transform.location = gmath.resolve_collision(owner_transform.location, owner_transform.scale, other_transform.location, other_transform.scale)       
   


#render component
#used to draw textures for a game object onto the screen
#can store animations and play those animations
class render_component(component):
    def __init__(self, owner, window:pg.surface, texture_file:str, transform:transform_component, frame_rate:float):
        super().__init__(owner)
        self.window = window
        self.transform = transform
        self.texture = Load_Texture(texture_file)
        self.animations = {}
        self.current_animation = []
        self.is_looping = True
        self.current_frame = 0
        self.elapsed_time = 0
        self.frame_rate = frame_rate
        self.flipped_x = False
        self.flipped_y = False

    #add animation via a list of image files
    def add_animation(self, name: str, textures):
        self.animations[name] = textures
        if len(self.animations) == 1:
            self.current_animation = self.animations[name]

    #play animation from animations list given a string name
    def play_animation(self, name: str, looping: bool):
        if name in self.animations:
            self.current_animation = self.animations[name]
            self.update_texture(self.current_animation[0])
            self.current_frame = 0
            self.elapsed_time = 0
            self.is_looping = looping

    #used if no animations exist to change the texture
    def update_texture(self, texture_file:str):
        self.texture = Load_Texture(texture_file)

    #update animation if playing an animation, otherwise just draw texture
    def Update(self, delta_time:float, world:game):
        if len(self.animations) > 0:
            self.elapsed_time += (delta_time * 1000)
            if self.elapsed_time >= self.frame_rate:
                self.elapsed_time = 0
                self.current_frame += 1
                if self.current_frame >= len(self.current_animation):
                    if not self.is_looping and 'default' in self.animations:
                        self.play_animation('default', True)
                    else:
                        self.current_frame = 0
                self.texture = Load_Texture(self.current_animation[self.current_frame])
        self.Draw()

    #draws current texture
    def Draw(self):
        current_texture = pg.transform.flip(self.texture, self.flipped_x, self.flipped_y)
        Draw_Sprite(self.window, current_texture, self.transform.location, self.transform.scale)



    




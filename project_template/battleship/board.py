"""Will handle the output and control of the program
    Board is a subclass of view.
    on_show will set up the board.
    on_draw will draw the sprites.
    on_update will update the board.
    splite_enemy will handle the enemy spliting.
    on_key_press will handle user input.
    on_key_relase will hadle when the user relases the key
    on_mouse_press will hadle the bullet from the user imput
"""
from ship import Ship
import arcade
import constants
from enemy import Enemy_icon
from pathlib import Path
from score import Score
from game_over_screen import Game_Over_Screen
import math
import random

#for collisions
from typing import cast

class Board(arcade.View):
    """Handles the output of the board. Along with the key inputs of the ship
    
    Code Based on:
        # https://arcade.academy/examples/sprite_collect_coins_background.html?highlight=background%20images
        # enemy behavior and functionality was based on https://github.com/daviddelsol1998/Slime_Space_invaders 
        which is in essence an over customized version of the above tutorials with other code from additional sources
        please see detailed informmation in the description within the enemy class.

    Stereotype:
        Controller/ Coordinator

    Authors:
        Spencer Wigren
        Logan Huston
        Josh Staples
        David Del Sol

    """

    def __init__(self):
        """The set up of the board.

        Args:
            ship_list = list of ships

        """
        super().__init__()

        # Path declaration for images to be loaded from.
        self.cur_dir = Path(__file__).parent
        self.assets_dir = self.cur_dir/"assets"

        # varables that will hold future spriteLists
        self.ship_list = None
        self.enemy_list = None
        self.enemy_ship_list = arcade.SpriteList()
        self.bullet_list = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        
        self.output_Score = Score()

        #Sounds
        #these ones are triggered when coallision happens
        self.hit_sound1 = arcade.load_sound(":resources:sounds/coin1.wav")
        self.hit_sound2 = arcade.load_sound(":resources:sounds/coin2.wav")
        self.hit_sound3 = arcade.load_sound(":resources:sounds/coin3.wav")
        self.hit_sound4 = arcade.load_sound(":resources:sounds/coin4.wav")
        self.background_music = arcade.load_sound(":resources:music/1918.mp3")

        arcade.play_sound(self.background_music)

        # Track the current state of what key is pressed
        self.a_pressed = False
        self.d_pressed = False
        self.w_pressed = False
        self.s_pressed = False
                
    def on_show(self):
        """Set up of the board.

        Args:
            self.ship_list = instance of ship class
            self.enemy_list = instance of enemy
            self.bullet_list = instance of bullet
        """
        #score
        self.score = 0

        # Sprite Lists
        self.ship_list = arcade.SpriteList()  
        self.enemy_list = arcade.SpriteList() 
        self.bullet_list = arcade.SpriteList() 

        self.player_ship = Ship(self.assets_dir / "motor-boat_1f6e5-fe0f.png", constants.SPRITE_SCALING)
        self.player_ship.center_x = constants.SCREEN_WIDTH/2
        self.player_ship.center_y = constants.SCREEN_HEIGHT/2
        self.ship_list.append(self.player_ship)

        # All enemy images
        image_list = (self.assets_dir / "enemy1.png",
                      self.assets_dir / "enemy2.png",
                      self.assets_dir / "enemy3.png",
                      self.assets_dir / "enemy4.png")

        for i in range(constants.STARTING_ENEMY_COUNT):
            enemy_sprite = Enemy_icon(self.assets_dir / "enemy1.png", constants.SCALE * 1.5)
            enemy_sprite.guid = "Enemy"

            enemy_sprite.center_y = random.randrange(constants.BOTTOM_LIMIT, constants.TOP_LIMIT)
            enemy_sprite.center_x = random.randrange(constants.LEFT_LIMIT, constants.RIGHT_LIMIT)

            enemy_sprite.change_x = random.random() * 3 - 1
            enemy_sprite.change_y = random.random() * 3 - 1

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.enemy_ship_list.append(enemy_sprite)


    def on_draw(self):
        """Draws the board

        Args:
            output_score.on_draw = instance of score class
        """
        arcade.start_render()

        # Draw all the Sprites 
        self.ship_list.draw() 
        self.bullet_list.draw()
        self.enemy_ship_list.draw()
        
        self.output_Score.on_draw()

    def on_update(self, delta_time):
        """updates the board including player movement. This is more seamlessly done in update than on key pressed. 
        Used with modification from: https://arcade.academy/examples/sprite_move_keyboard_better.html

        Args:
            None
        """

        # Calculate speed based on the keys pressed
        self.player_ship.change_x = 0
        self.player_ship.change_y = 0

        if self.w_pressed and not self.s_pressed:
            self.player_ship.change_y = constants.MOVEMENT_SPEED
        elif self.s_pressed and not self.w_pressed:
            self.player_ship.change_y = -constants.MOVEMENT_SPEED
        if self.a_pressed and not self.d_pressed:
            self.player_ship.change_x = -constants.MOVEMENT_SPEED
        elif self.d_pressed and not self.a_pressed:
            self.player_ship.change_x = constants.MOVEMENT_SPEED

        # Call update to move the sprite
        # If using a physics engine, call update player to rely on physics engine
        # for movement, and call physics engine here.
        self.player_ship.update()

        self.enemy_ship_list.update()
        self.bullet_list.update()

        # Loop through each bullet
        for bullet in self.bullet_list:
            enemies = arcade.check_for_collision_with_list(bullet, self.enemy_ship_list)

            # # For every coin (enemy) we hit, add to the score and remove the coin
            for enemy in enemies:
                self.split_enemy(cast(Enemy_icon, enemy))  # expected Enemy_icon, got Sprite instead
                enemy.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > constants.SCREEN_WIDTH or bullet.top < 0 or bullet.right < 0 or bullet.left > constants.SCREEN_WIDTH:
                bullet.remove_from_sprite_lists()

        if arcade.check_for_collision_with_list(self.player_ship, self.enemy_ship_list):
            """Put game over screen here"""    
            #Will need to change how to access the file and run that file.
            game_over_view = Game_Over_Screen()
            game_over_view.final_score = self.output_Score.get_score()
            self.window.show_view(game_over_view)



    def split_enemy(self, enemy: Enemy_icon):
        """ Split an enemy into smaller versions.
        
        Args:
            x = enemy location 
            y = enemy location
            self.score = instance of score class
        """
        
        x = enemy.center_x
        y = enemy.center_y
        self.score += 1

        if enemy.size == 4:
            for i in range(3):
                enemy_sprite = Enemy_icon(self.assets_dir / "enemy2.png", constants.SCALE * 1.5)
                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 2.5 - 1.25
                enemy_sprite.change_y = random.random() * 2.5 - 1.25

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 3

                self.enemy_ship_list.append(enemy_sprite)
                self.hit_sound1.play()

            # Will update the score
            self.output_Score.update_basic()

        elif enemy.size == 3:
            for i in range(3):
                enemy_sprite = Enemy_icon(self.assets_dir / "enemy3.png", constants.SCALE * 1.5)
                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3 - 1.5
                enemy_sprite.change_y = random.random() * 3 - 1.5

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 2

                self.enemy_ship_list.append(enemy_sprite)
                self.hit_sound2.play()

            # Will update the score
            self.output_Score.update_basic()

        elif enemy.size == 2:
            for i in range(3):
                enemy_sprite = Enemy_icon(self.assets_dir / "enemy4.png", constants.SCALE * 1.5)
                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3.5 - 1.75
                enemy_sprite.change_y = random.random() * 3.5 - 1.75

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 1

                self.enemy_ship_list.append(enemy_sprite)
                self.hit_sound3.play()

            # Will update the score
            self.output_Score.update_basic()

        elif enemy.size == 1:
            # Will play the last sound
            self.hit_sound4.play()

            # Will update the score
            self.output_Score.update_final()
            
    def on_key_press(self, key, modifiers):
        """Handles the key press and movement
        called whenever a key is pressed. 

        Args:
            key = What the key is
        """

        # If the player presses a key, update the speed
        if key == arcade.key.W:
            self.w_pressed = True
        elif key == arcade.key.S:
            self.s_pressed = True
        elif key == arcade.key.A:
            self.a_pressed = True
        elif key == arcade.key.D:
            self.d_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key.
        
        Args:
            key = What the key is
        """

        # If a player releases a key, zero out the speed.
        # This doesn't work well if multiple keys are pressed.
        # Use 'better move by keyboard' example if you need to
        # handle this.
        if key == arcade.key.W:
            self.w_pressed = False
        elif key == arcade.key.S:
            self.s_pressed = False
        elif key == arcade.key.A:
            self.a_pressed = False
        elif key == arcade.key.D:
            self.d_pressed = False      

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. 
        
        Taken from: https://arcade.academy/examples/sprite_bullets_aimed.html#sprite-bullets-aimed
        with slight modification of Sprite names.
        
        Args:
            bullet = sprite of bullet, instance of enemy
            start_x = player locaton
            start_y = player location

        """

        # Create a bullet
        bullet = arcade.Sprite(self.assets_dir / "laserRed01.png", constants.SPRITE_SCALING_LASER)

        # Position the bullet at the player's current location
        start_x = self.player_ship.center_x
        start_y = self.player_ship.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.
        dest_x = x
        dest_y = y

        # Do math to calculate how to get the bullet to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Angle the bullet sprite so it doesn't look like it is flying
        # sideways.
        bullet.angle = math.degrees(angle)
        # print(f"Bullet angle: {bullet.angle:.2f}")

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        bullet.change_x = math.cos(angle) * constants.BULLET_SPEED
        bullet.change_y = math.sin(angle) * constants.BULLET_SPEED

        # Add the bullet to the appropriate lists
        self.bullet_list.append(bullet)
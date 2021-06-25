import os
import os.path
import pygame

import configurator
import frame_buffer

import json
import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str


# Grimy ass globals because fuck it.
data = None               # Calibration data for Analog stick values
m_data = None             # Calibration data for Mode-shifted stick values
mflags = None             # Dictionary of flags representing which modifiers are enabled or disabled
mask = None               # Dictionary of mask values used to determine valid directions for a given modifier
last_mods = (None, None)  # These are not specific to an instance of the StickImage class so it's separated
last_xy = None
button_obj = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
shield_buttons = [None, None, None, None]
shield_values = [0, 0]    # Previous L/R values used for determining if either value has changed
loaded = False
map_flags = {}            # This is used to tell if Tilt3, X3, or Y3 are mapped or if 1 + 2 was used.

# Dictionaries used for referencing button and shield indexes
get_button_index = {'left':2, 'right':3, 'up':4, 'down':5, 'T2':6, 'T':7, 'X1':8, 'X2':9, 'Y1':10, 'Y2':11, 'M':12,
                    'LS':13, 'L':13, 'R':13, 'ST':13, 'Mode':14, 'X3':15, 'Y3':16, 'T3':17}
get_shield_index = {'LS':0, 'ST':0, 'L':1, 'R':2}

def isclose(a, b, rel_tol=1e-04, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class ButtonImage:
    all = list()

    def __init__(self, screen, background, position, size, image_push=None,
                 image_free=None, margin=0, auto_rect=True, copy_bg=False,
                 copy_fg=False):
        self.target = screen
        self.image_push = image_push
        self.image_free = image_free
        self.image = self.image_free or self.image_push
        if self.image is None:
            raise ValueError
        self.position = tuple(position)
        self.size = pygame.Rect((0, 0), tuple(size))
        self.rect = self.size.copy()
        self.rect.center = self.position  # TODO: is centering this correct?
        if auto_rect:
            self.rect = self.image.get_rect(center=self.position)
        self.position = self.rect.topleft
        self.domain_rect = self.rect.inflate(margin * 2, margin * 2).clip(
            self.target.get_rect())
        self.foreground = None
        self.background = None
        if background is not None:
            if copy_fg:
                self.foreground = background.subsurface(self.domain_rect).copy()
            if copy_bg:
                self.background = screen.subsurface(self.domain_rect).copy()
            if self.image_push is None:
                self.image_push = background.subsurface(self.rect).copy()
            if self.image_free is None:
                self.image_free = background.subsurface(self.rect).copy()
        self.image = self.image_free
        ButtonImage.all.append(self)
        self.dirty = True

    def push(self, value):
        if value > 0.05:        # How much tilt is necessary to register as tilted for the Analog/C-stick
           self._press()
        else:
           self._release()

    def _press(self):
        if self.image is not self.image_push:
            self.image = self.image_push
            self.dirty = True

    def _release(self):
        if self.image is not self.image_free:
            self.image = self.image_free
            self.dirty = True

    def draw(self, force=False):
        if self.dirty or force:
            if self.background:
                self.target.blit(self.background, self.domain_rect)
            self.target.blit(self.image, self.position, area=self.size)
            if self.foreground:
                self.target.blit(self.foreground, self.domain_rect)
            self.dirty = False

    def erase(self, force=False):
        self.image = self.image_free
        ButtonImage.draw(self)


class StickImage(ButtonImage):
    class Direction:
        def __init__(self, parent):
            self.value = 0
            self.parent = parent

        def push(self, value):
            if self.value != value:
                self.value = min(1, max(0, value))
                self.parent.dirty = True

    def __init__(self, screen, background, position, size, radius, image_stick, image_free=None, image_clear=None):
        global loaded
        global data
        global m_data
        self.data = {}
        self.m_data = {}
        self.radius = int(radius)
        self.frame_counter = 0
        self.image_stick = image_stick
        self.image_free = image_free
        self.image_clear = image_clear
        self.directions = {'up': StickImage.Direction(self),
                           'down': StickImage.Direction(self),
                           'left': StickImage.Direction(self),
                           'right': StickImage.Direction(self),
                           'click': self}
        self.modifiers = ['Full', 'Tilt', 'Tilt2', 'Tilt3', 'X1', 'X2', 'X3', 'Y1', 'Y2', 'Y3', 'Mode']

        #   2     3    4     5   6   7   8   9  10  11  12  13   <-- button indices
        # left, right, up, down, t2, t, x1, x2, y1, y2, m, ls    <-- button objects

        # Used for drawing modifier buttons as being pressed
        self.mod_draw = ((0, 0),(8, 0),(9, 0),(8,9),(10, 0),(11, 0),(10,11),(6, 0),(7, 0))
        # Used for drawing directional buttons as being pressed
        self.dir_draw = ((None, None),(2,5),(5, None),(3,5),(2, None), (None, None),(3, None), (2,4),(4, None),(3,4))
        # Used for clearing directional buttons ???
        self.dir_clear = ((2, 3, 4, 5),(3,4, None, None),(2, 3, 4, None),(2,4, None, None),(3, 4, 5, None),
                     (2,3,4,5),(2, 4, 5, None),(3,5, None, None),(2, 3, 5, None),(2,5, None, None))
        ButtonImage.__init__(self, screen, background, position, size,
                             image_stick, image_free, margin=self.radius,
                             copy_bg=True)

    def reset(self):
        for direction in self.directions.itervalues():
            direction.push(0)

    def draw(self, force=False):
        global button_obj
        global last_mods
        global last_xy

        if self.dirty or force:
            if not loaded:
                return
            x = self.directions['right'].value - self.directions['left'].value
            y = self.directions['down'].value - self.directions['up'].value

            # Make sure that we've loaded the data
            if not loaded:
                return

            # Make sure that we've made the data members independent references
            if not self.data:
                for value in self.modifiers:
                    if value != 'Mode':
                        if data:
                            if data.has_key(value):
                                self.data[value] = data[value].copy()
                                self.m_data[value] = m_data[value].copy()

            # If x and y are exactly zero then initialize them to the neutral stick position
            if(x == 0):
                x = self.data['Full']['Neutral'][0]
            if(y == 0):
                y = self.data['Full']['Neutral'][1]

            # Keeps track of the recency of "Last" modifier
            self.frame_counter += 1
            if self.frame_counter >= 100:
                self.frame_counter = 0
                last_mods = (None, None)

            # Skip duplicate input frames
            if last_xy == (x,y):
                return
            else:
                last_xy = (x,y)

            # This section sets the x and y flags and polarity values and detects if mode is being used.
            # The x and y flags and polarity have been separated to make dealing with combinations more
            # easily manageable.
            def analyze_inputs():
                global data
                global m_data
                global last_mods

                neutral_x, neutral_y = self.data['Full']['Neutral']
                neutral_mode_x, neutral_mode_y = self.m_data['Full']['Neutral']
                found_x = False
                found_y = False
                found_mode_x = False
                found_mode_y = False
                modifier_x = 'Full'
                modifier_y = 'Full'
                modifier_mode_x = 'Full'
                modifier_mode_y = 'Full'

                # Check if stick is neutral in either direction
                if x != neutral_x:
                    if x < neutral_x:
                        polarity_x = 'Left'
                    else:
                        polarity_x = 'Right'
                else:
                    polarity_x = 'Neutral'

                if y != neutral_y:
                    if y < neutral_y:
                        polarity_y = 'Up'
                    else:
                        polarity_y = 'Down'
                else:
                    polarity_y = 'Neutral'

                # Check if Mode is neutral in either direction
                if x != neutral_mode_x:
                    if x < neutral_mode_x:
                        polarity_mode_x = 'Left'
                    else:
                        polarity_mode_x = 'Right'
                else:
                    polarity_mode_x = 'Neutral'
                if y != neutral_mode_y:
                    if y < neutral_mode_y:
                        polarity_mode_y = 'Up'
                    else:
                        polarity_mode_y = 'Down'
                else:
                    polarity_mode_y = 'Neutral'

                mirrored = False
                flipped = False
                inverted = False

                # First detect if Mode is Mirroring across the horizontal axis
                if self.m_data['Full']['Left'] > self.m_data['Full']['Right']:
                    mirrored = True
                    if polarity_mode_x == 'Left':
                        polarity_mode_x = 'Right'
                    elif polarity_mode_x == 'Right':
                        polarity_mode_x = 'Left'
                # Second detect if Mode is Inverting across the vertical axis
                if self.m_data['Full']['Up'] > self.m_data['Full']['Down']:
                    flipped = True
                    if polarity_mode_y == 'Up':
                        polarity_mode_y = 'Down'
                    elif polarity_mode_y == 'Down':
                        polarity_mode_y = 'Up'
                if mirrored and flipped:
                    inverted = True

                # Counts the number of non-neutral directional inputs being provided
                dirs = 0
                if polarity_x != 'Neutral':
                    dirs += 1
                else:
                    found_x = True
                    modifier_x = 'Full'
                if polarity_y != 'Neutral':
                    dirs += 1
                else:
                    found_y = True
                    modifier_y = 'Full'

                # Counts the number of Mode-shifted non-neutral directional inputs being provided
                dirs_mode = 0
                if polarity_mode_x != 'Neutral':
                    dirs_mode += 1
                else:
                    found_mode_x = True
                    modifier_mode_x = 'Full'
                if polarity_mode_y != 'Neutral':
                    dirs_mode += 1
                else:
                    found_mode_y = True
                    modifier_mode_y = 'Full'

                # Combine polarities to get absolute stick direction:
                if dirs >= 2:
                    abs_direction = polarity_y + '-' + polarity_x
                elif dirs == 1:
                    if polarity_x != 'Neutral':
                        abs_direction = polarity_x
                    else:
                        abs_direction = polarity_y
                else:
                    abs_direction = 'Neutral'

                # Combine Mode-shifted polarities to get absolute stick direction:
                if dirs_mode >= 2:
                    abs_mode_direction = polarity_mode_y + '-' + polarity_mode_x
                elif dirs_mode == 1:
                    if polarity_mode_x != 'Neutral':
                        abs_mode_direction = polarity_mode_x
                    else:
                        abs_mode_direction = polarity_mode_y
                else:
                    abs_mode_direction = 'Neutral'

                # Check all modifiers in abs_direction and abs_mode_direction
                # Modifier priority is: Full -> Last Used -> X/Y -> Tilts -> Mode
                # Check all modifiers and keeps priority unless exact match is found. Always go with the exact match.
                for modifier in ['Full', last_mods[0], last_mods[1], 'X3', 'X2', 'X1', 'Y3', 'Y2', 'Y1', 'Tilt2', 'Tilt', 'Tilt3']:
                    if modifier and self.data.has_key(modifier):
                        if self.data[modifier].has_key(abs_direction):
                            if x == self.data[modifier][abs_direction][0]:
                                if y == self.data[modifier][abs_direction][1]:
                                    modifier_x = modifier
                                    modifier_y = modifier
                                    found_x = True
                                    found_y = True
                                    break
                            if not found_x:
                                if x == self.data[modifier][abs_direction][0]:
                                    modifier_x = modifier
                                    found_x = True
                            if not found_y:
                                if y == self.data[modifier][abs_direction][1]:
                                    modifier_y = modifier
                                    found_y = True
                            #if found_x and found_y:
                            #    break

                # Check all Mode-shifted modifiers
                if not found_x or not found_y:
                    for modifier in ['Full', last_mods[0], last_mods[1], 'X3', 'X2', 'X1', 'Y3', 'Y2', 'Y1', 'Tilt2', 'Tilt', 'Tilt3']:
                        #print abs_direction, abs_mode_direction
                        mode_direction = abs_mode_direction
                        if modifier in ['Tilt', 'Tilt2', 'Tilt3', 'X1', 'X2', 'X3', 'Y1', 'Y2', 'Y3']:
                            mode_direction = abs_direction                          # Don't invert Tilts or XY mods
                        if modifier and self.m_data.has_key(modifier):
                            if self.m_data[modifier].has_key(mode_direction):
                                if x == self.m_data[modifier][mode_direction][0]:
                                    if y == self.m_data[modifier][mode_direction][1]:
                                        modifier_mode_x = modifier
                                        modifier_mode_y = modifier
                                        found_mode_x = True
                                        found_mode_y = True
                                        print "FOUND EXACT MATCH: {}".format(modifier)
                                        break
                                if not found_mode_x:
                                    if x == self.m_data[modifier][mode_direction][0]:
                                        modifier_mode_x = modifier
                                        found_mode_x = True
                                        print "FOUND X: {}".format(modifier)
                                if not found_mode_y:
                                    if y == self.m_data[modifier][mode_direction][1]:
                                        modifier_mode_y = modifier
                                        found_mode_y = True
                                        print "FOUND Y: {}".format(modifier)
                                # if found_mode_x and found_mode_y:
                                #     break

                # Check which modifiers match for each direction and update the last modifiers list
                if found_x and found_y:
                    if modifier_x == modifier_y:
                        if 'Full' != modifier_x:
                            last_mods = (modifier_x, None)
                        display_message_single(modifier_x, polarity_x, polarity_y, abs_direction, False)
                    else:
                        if 'Full' not in [modifier_x, modifier_y]:
                            last_mods = (modifier_x, modifier_y)
                        display_message_multiple(modifier_x, modifier_y, polarity_x, polarity_y, abs_direction, False)
                elif found_mode_x and found_mode_y:
                    # Make sure it doesn't switch the directions for tilts or modifiers!
                    if modifier_mode_x in ['Tilt', 'Tilt2', 'Tilt3', 'X1', 'X2', 'X3', 'Y1', 'Y2', 'Y3']:
                        polarity_mode_x = polarity_x
                    if modifier_mode_y in ['Tilt', 'Tilt2', 'Tilt3', 'X1', 'X2', 'X3', 'Y1', 'Y2', 'Y3']:
                        polarity_mode_y = polarity_y
                    if modifier_mode_x == modifier_mode_y:
                        if 'Full' != modifier_mode_x:
                            last_mods = (modifier_mode_x, None)
                        display_message_single(modifier_mode_x, polarity_mode_x, polarity_mode_y, abs_mode_direction, True)
                    else:
                        if 'Full' not in [modifier_mode_x, modifier_mode_y]:
                            last_mods = (modifier_mode_x, modifier_mode_y)
                        display_message_multiple(modifier_mode_x, modifier_mode_y, polarity_mode_x, polarity_mode_y, abs_mode_direction, True)
                else:
                    print('FAILURE: Unable to match directional inputs to a Modifier! X: {}, Y: {}, Direction: {}').format(x,y,abs_mode_direction)

            # Output the button presses to console when only a single modifier or no modifiers present
            def display_message_single(xy_modifier, x_dir, y_dir, xy_dir, mode):
                message = ''
                if mode:
                    message = 'Mode && '
                if xy_dir != 'Neutral':
                    if xy_modifier == 'Full':
                        message = message + xy_dir
                    else:
                        message = message + xy_dir + ' && ' + xy_modifier + '!'
                    print '{}, ({},{})'.format(message, x, y)
                    #print message
                else:
                    print 'Neutral'
                draw_buttons_single(xy_modifier, x_dir, y_dir, xy_dir, mode)

            # Output the button presses to console
            def display_message_multiple(x_modifier, y_modifier, x_dir, y_dir, xy_dir, mode):
                message = ''
                if mode:
                    message = 'Mode && '
                message = message + xy_dir + ' && ' + x_modifier + ' && ' + y_modifier + '!'
                print '{}, ({},{})'.format(message, x, y)
                #print message
                draw_buttons_multiple(x_modifier, y_modifier, x_dir, y_dir, xy_dir, mode)

            # Display a combination of buttons that uses a single modifier
            def draw_buttons_single(xy_modifier, x_dir, y_dir, xy_dir, mode):
                draw_buttons_multiple(xy_modifier, None, x_dir, y_dir, xy_dir, mode)

            # Display a combination of buttons that uses multiple modifiers
            def draw_buttons_multiple(x_modifier, y_modifier, x_dir, y_dir, xy_dir, mode):
                get_keys = {'Down-Left':(2,5), 'Down':(5,None), 'Down-Right':(3,5), 'Left':(2,None),
                            'Neutral':(None,None), 'Right':(3,None), 'Up-Left':(2,4), 'Up':(4,None), 'Up-Right':(3,4)}
                get_modifiers = {'Full':(None,None), 'Tilt':(7,None), 'Tilt2':(6,None), 'Tilt3':(7,6),
                                 'X1':(8,None), 'X2':(9,None), 'X3':(8,9), 'Y1':(10,None), 'Y2':(11,None), 'Y3':(10,11), 'Mode':12}
                # BUTTON INDICES:   2     3    4     5   6   7   8   9  10  11  12  13
                # BUTTON OBJECTS: left, right, up, down, t2, t, x1, x2, y1, y2, mode, ls

                # Draw all directional buttons being pressed
                direction_1 = get_keys[x_dir]
                if y_dir:
                    direction_2 = get_keys[y_dir]
                else:
                    direction_2 = (None,None)
                for i in direction_1 + direction_2:
                    if i:
                        button_obj[i].target.blit(button_obj[i].image_push, button_obj[i].position)
                        button_obj[i].draw()

                # Unload the unpressed directional buttons
                combined_dirs = get_keys[x_dir]
                if y_dir:
                    combined_dirs = combined_dirs + get_keys[y_dir]
                for k in range(2,6):
                    if k not in combined_dirs:
                        if button_obj[k]:
                            button_obj[k].target.blit(button_obj[k].image_free, button_obj[k].position)
                            button_obj[k].draw()

                # Get the combined modifiers and draw them
                global map_flags
                # This is so that it presses 3 unless it isn't mapped and presses 1 + 2 instead
                if (x_modifier == 'Tilt3' and map_flags.has_key('Tilt3')) \
                    or (x_modifier == 'X3' and map_flags.has_key('X3'))   \
                    or (x_modifier == 'Y3' and map_flags.has_key('Y3')):
                    combined = get_button_index[x_modifier]
                else:
                    combined = get_modifiers[x_modifier]
                # Do the same for the second modifier detected
                if get_modifiers.has_key(y_modifier):
                    if (y_modifier == 'Tilt3' and map_flags.has_key('Tilt3')) \
                            or (y_modifier == 'X3' and map_flags.has_key('X3')) \
                            or (y_modifier == 'Y3' and map_flags.has_key('Y3')):
                        combined = get_button_index[y_modifier]
                    else:
                        combined = combined + get_modifiers[y_modifier]
                for j in combined:
                    if j:
                        button_obj[j].target.blit(button_obj[j].image_push, button_obj[j].position)
                        button_obj[j].draw()
                for k in range(6,len(button_obj)):
                    if k not in combined:
                        if k != 12 and k != 13:
                            if button_obj[k]:
                                button_obj[k].target.blit(button_obj[k].image_free, button_obj[k].position)
                                button_obj[k].draw()

                # Draw or unload the Mode button as necessary
                m_index = get_modifiers['Mode']
                if mode:
                    button_obj[m_index].target.blit(button_obj[m_index].image_push, button_obj[m_index].position)
                    button_obj[m_index].draw()
                else:
                    button_obj[m_index].target.blit(button_obj[m_index].image_free, button_obj[m_index].position)
                    button_obj[m_index].draw()

            #get_image_from_modifier = {1:8, 2:9, 4:10, 5:11, 7:6, 8:7}
            #                  0    1   2  3   4   5    6   7      8     9
            #x and y flags = [full, X1, X2, X3, Y1, Y2, Y3, tilt2, tilt, tilt3]
            analyze_inputs()


class TriggerImage(ButtonImage):
    def __init__(self, screen, background, name, position, size, depth,
                 image_push, image_free):
        self.depth = int(depth)
        self.value = 0.0
        self.redraws = set()
        self.name = name
        self.image_push = image_push
        ButtonImage.__init__(self, screen, background, position, size,
                             image_push, image_free, margin=self.depth,
                             auto_rect=False, copy_bg=True, copy_fg=True)

    def push(self, value, silent=False):
        global shield_buttons
        global shield_values
        max_dead_zone = .03  # Dead zones so that innacurate Zadig & GCN USB Feeder L/R detection to work properly
        min_dead_zone = .03  # Dead zones so that innacurate Zadig & GCN USB Feeder L/R detection to work properly

        self.target.blit(self.image_free, self.position) # Initially draws all L/R/LS buttons in released state.
        if not silent:
            print "Shielding changed! Old: {}, New: {}, Name: {}".format(self.value, value, self.name)
        if self.value != value:                          # Update the appropriate shield value.
            if self.name == 'L':
                shield_values[0] = value
            elif self.name == 'R':
                shield_values[1] = value
        self.value = value
        if self.name == 'L':
            if value >= 1.0-max_dead_zone:
                self.target.blit(self.image_push, self.position)
                shield_buttons[0].push(0)
            elif value <= 0+min_dead_zone:
                self.target.blit(self.image_free, self.position)
                shield_buttons[0].push(0)
            else:
                self.target.blit(self.image_free, self.position)
                shield_buttons[0].push(1)
        if self.name == 'R':
            if value >= 1.0-max_dead_zone:
                self.target.blit(self.image_push, self.position)
            else:
                self.target.blit(self.image_free, self.position)

    def update_redraws(self):
        assert isinstance(self, TriggerImage)
        self.value = .5
        self.draw(True)
        self.push(0, True)

    def draw(self, force=False):
        if self.dirty or force:
            ButtonImage.draw(self, force)
            # for b in self.redraws:
            #   b.draw(force=True)

class EmptyPadImage:
    def __init__(self, cfg, screen):
        assert isinstance(cfg, configurator.PadConfig)
        self.path = cfg.path

        def load_image(name):
            return pygame.image.load(os.path.join(cfg.path, '%s.png' % name))

        self.target = screen
        self.target.fill(cfg.background_color)
        self.background = load_image(cfg.background + '-unmapped')
        self.target.blit(self.background, (0, 0))

        # Initialize the images
        if os.path.isfile(cfg.path + '\Transparent.png'):
            image_clear = load_image(str("Transparent"))
        screen.flip()


class PadImage:
    def __init__(self, cfg, screen):
        assert isinstance(cfg, configurator.PadConfig)
        self.buttons = dict()
        self.triggers = dict()
        self.sticks = dict()
        self.path = cfg.path

        # grimy globals because meh
        global button_obj
        global shield_buttons

        def load_image(name):
            return pygame.image.load(os.path.join(cfg.path, '%s.png' % name))

        self.target = screen
        self.target.fill(cfg.background_color)
        self.background = load_image(cfg.background)
        self.target.blit(self.background, (0, 0))

        # Initialize the images
        if os.path.isfile(cfg.path + '\Transparent.png'):
            image_clear = load_image(str("Transparent"))

        for button_cfg in cfg.buttons.itervalues():
            assert isinstance(button_cfg, configurator.ButtonConfig)
            image_push = load_image(button_cfg.name)
            image_free = load_image(button_cfg.name + '-2')
            obj = ButtonImage(self.target, self.background,
                              button_cfg.position, button_cfg.size, image_push, image_free)
            self.buttons[button_cfg.name] = obj
            if get_button_index.has_key(button_cfg.name):
                index = get_button_index[button_cfg.name]
            else:
                index = None
            if index == 13:
                index = get_shield_index[button_cfg.name]
                shield_buttons[index] = obj
            elif index:
                button_obj[index] = obj
                #print "Storing button: {} at index: {}".format(button_cfg.name, index)

        for stick_cfg in cfg.sticks.itervalues():
            assert isinstance(stick_cfg, configurator.StickConfig)
            image_stick = load_image(stick_cfg.name)
            image_free = load_image(stick_cfg.name + '-2')
            obj = StickImage(self.target, self.background,
                             stick_cfg.position, stick_cfg.size,
                             stick_cfg.radius, image_stick, image_free, image_clear)
            self.sticks[stick_cfg.name] = obj


        for trigger_cfg in cfg.triggers.itervalues():
            assert isinstance(trigger_cfg, configurator.TriggerConfig)
            image_push = load_image(trigger_cfg.name)
            image_free = load_image(trigger_cfg.name + '-2')
            obj = TriggerImage(self.target, self.background, trigger_cfg.name,
                               trigger_cfg.position, trigger_cfg.size,
                               trigger_cfg.depth, image_push, image_free)
            self.triggers[trigger_cfg.name] = obj
            index = get_shield_index[trigger_cfg.name]
            shield_buttons[index] = obj

        for trigger in self.triggers.itervalues():
            trigger.update_redraws()


    def draw(self):
        for button in self.buttons.itervalues():
            assert isinstance(button, ButtonImage)
            button.draw()
        for stick in self.sticks.itervalues():
            assert isinstance(stick, StickImage)
            stick.draw()
        for trigger in self.triggers.itervalues():
            assert isinstance(trigger, TriggerImage)
            trigger.draw()


def _get_target(pad_gfx, map_element):
    elt_type = map_element['type']
    elt_name = map_element['name']
    target = None
    if elt_type == 'button':
        if not pad_gfx.buttons.has_key(elt_name):
            print "ERROR: Detected a depressed key which is not currently mapped!"
        #assert pad_gfx.buttons.has_key(elt_name)
        target = pad_gfx.buttons[elt_name]
    elif elt_type == 'trigger':
        target = pad_gfx.triggers[elt_name]
    elif elt_type == 'stick':
        which = map_element['direction']
        target = pad_gfx.sticks[elt_name].directions[which]
    assert target is not None
    return target

def load_stick_data(pad_gfx):
    # Load the global stick values
    global mflags
    global loaded
    global data
    global m_data
    global mask

    # Load the data from the JSON file
    with open(pad_gfx.path + '\stick_data.json') as data_file:
        data_loaded = json.load(data_file)
    print("Calibration data has been loaded!")

    data = data_loaded['stick_data']
    m_data = data_loaded['mode_data']
    mflags = data_loaded['mflags']
    mask = data_loaded['stick_mask']
    loaded = True
    print "Mapping and Calibration data has been successfully loaded!"
    return

def load_map_flags(pad_gfx):
    global map_flags
    # Load the data from the JSON file
    with open(pad_gfx.path + '\\flags.json') as data_file:
        map_flags = json.load(data_file)
    return

def main(skin, joy_index):
    pygame.display.init()
    pygame.joystick.init()

    joy = pygame.joystick.Joystick(joy_index)
    joy.init()
    mappings = configurator.load_mappings(skin)
    if joy.get_name() not in mappings:
        print 'Please run the mapper on', joy.get_name(), 'with', skin, 'skin.'
        return

    mappings = mappings[joy.get_name()]
    button_map = mappings.get('button', dict())
    axis_map = mappings.get('axis', dict())
    pad_cfg = configurator.PadConfig(skin)
    fb = frame_buffer.FrameBuffer(pad_cfg.size, pad_cfg.size,
                                  scale_smooth=pad_cfg.anti_aliasing,
                                  background_color=pad_cfg.background_color)
    pad_gfx = PadImage(pad_cfg, fb)
    fb.flip()
    # Read in joystick and modifier calibration data from JSON file
    load_stick_data(pad_gfx)
    load_map_flags(pad_gfx)

    while not pygame.event.peek(pygame.QUIT):
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if str(event.button) in button_map:
                    elt = button_map[str(event.button)]
                    _get_target(pad_gfx, elt).push(1)
            elif event.type == pygame.JOYBUTTONUP:
                if str(event.button) in button_map:
                    elt = button_map[str(event.button)]
                    _get_target(pad_gfx, elt).push(0)
            elif event.type == pygame.JOYAXISMOTION:
                if str(event.axis) in axis_map:
                    for change, elt in axis_map[str(event.axis)].iteritems():
                        change = int(change)
                        value = event.value
                        if abs(change) == 2:
                            value += change / abs(change)
                        value /= change
                        value = max(0, value)
                        _get_target(pad_gfx, elt).push(value)
            fb.handle_event(event)
        pad_gfx.draw()
        fb.flip()
        fb.limit_fps(set_caption=True)

if __name__ == '__main__':
    main('smashbox', 0)

import os
import os.path
import pygame
import time

import configurator
import frame_buffer
import ctypes
import json
import io
import visualizer

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

# Used to store intermediate values for stick coordinates
stick_x = None
stick_y = None

# Used to store a reference to the various shielding button objects
shield_buttons = [None, None, None, None]


class CalibrationTests():
    def __init__(self):

        # Builds the data structure using dictionaries populated from lists. This allows for clear references to elements.
        self.directions = ['Down-Left', 'Down', 'Down-Right', 'Left', 'Neutral', 'Right', 'Up-Left', 'Up', 'Up-Right']
        self.ordered_directions = ['Neutral', 'Left', 'Up-Left', 'Up', 'Up-Right', 'Right', 'Down-Right', 'Down', 'Down-Left']
        x_directions = ['Left', 'Up-Left', 'Up-Right', 'Right', 'Down-Right', 'Down-Left']
        y_directions = ['Up-Left', 'Up', 'Up-Right', 'Down-Right', 'Down', 'Down-Left']

        # self.mask masks out directions that don't apply to a specific modifier
        self.mask = {'Full': self.directions, 'Tilt': self.directions, 'Tilt2': self.directions, 'Tilt3': self.directions,
                          'X1': x_directions, 'X2': x_directions, 'X3': x_directions,
                          'Y1': y_directions, 'Y2': y_directions, 'Y3': y_directions}
        self.modifiers = ['Full', 'Tilt', 'Tilt2', 'Tilt3', 'X1', 'X2', 'X3', 'Y1', 'Y2', 'Y3', 'Mode']

        # Initialize the empty dictionaries
        blank = {}
        x_blank = {}
        y_blank = {}
        self.data = {}
        self.m_data = {}
        self.mflags = {}
        self.get_keys = {}
        self.get_direction = {}

        # Build the dictionaries for data, mode_data, mflags, get_direction, and get_keys
        for value in x_directions:
            x_blank[value] = (0,0)                                # Build the X direction blank values
        for value in y_directions:
            y_blank[value] = (0,0)                                # Build the Y direction blank values
        for counter, value in enumerate(self.ordered_directions):
            blank[value] = (0,0)                                  # Build the X & Y direction blank values
        for counter, value in enumerate(self.directions):
            self.get_keys[value] = counter+1                      # Couple directions with keypad numbers
            self.get_direction[counter+1] = value                 # Couple directions with keypad numbers
        for counter, value in enumerate(self.modifiers):
            if value != 'Mode':                                   # Only add keys for directions that aren't masked out
                if any(value == m for m in ['Full', 'Tilt', 'Tilt2', 'Tilt3']):
                    self.data[value] = blank.copy()               # Set default calibration data for X & Y
                    self.m_data[value] = blank.copy()             # Set default mode calibration data for X & Y
                elif any(value == m for m in ['X1', 'X2', 'X3']):
                    self.data[value] = x_blank.copy()             # Set default calibration data for X direction
                    self.m_data[value] = x_blank.copy()           # Set default calibration data for X direction
                elif any(value == m for m in ['Y1', 'Y2', 'Y3']):
                    self.data[value] = y_blank.copy()             # Set default calibration data for Y direction
                    self.m_data[value] = y_blank.copy()           # Set default calibration data for Y direction
            self.mflags[value] = 1                                # Enable all modifiers by default


        # Since I'm using embedded Dictionaries with duplicate subkeys, we have to use copies to update values
        # otherwise changing one key ie 'Full' changes all keys because all keys share the same subkey names.
        data = self.data
        m_data = self.m_data

        # Perform a switcheroo such that self.data and self.m_data have independent data references now per key
        for value in self.modifiers:
            if value != 'Mode':
                self.data[value] = data[value].copy()
                self.m_data[value] = data[value].copy()

    def init_tests(self, pad_cfg, button_map, axis_map, fb):
        def Mbox(title, text, style):
            return ctypes.windll.user32.MessageBoxA(0, text, title, style)

        Mbox('Instructions:', 'This test records your control stick and modifier settings for smashbox.\n\n'
                              '1) Read the prompt for each test.\n'
                              '2) Answer Yes/No to perform or skip that test.\n'
                              '3) When testing, hold the required buttons and press \'A\'.\n', 0)

        MB_OK = 0
        MB_OKCANCEL = 1
        MB_YESNOCANCEL = 3
        MB_YESNO = 4
        IDOK = 0
        IDCANCEL = 2
        IDABORT = 3
        IDYES = 6
        IDNO = 7

        def run_test(mod_type, mode):
            def get_directions():
                global stick_x
                global stick_y
                direction = [None, 'Left/Down', 'Down', 'Right/Down', 'Left', 'all 4 directions to jumpstart polling and then let it go back to Neutral', 'Right', 'Left/Up', 'Up', 'Right/Up']
                punctuation = [' ', ' + ']

                if mode:
                    mode_text = ' + Mode '
                else:
                    mode_text = ''

                # Uses the mask to skip gathering data for directions that don't apply to a specific modifier
                for d in self.ordered_directions:
                    if (d == 'Neutral' and mod_type == 'Full') or d != 'Neutral':
                        name = ''
                        punct = punctuation[0]
                        if d in self.mask[mod_type]:
                            if mod_type != 'Full':
                                punct = punctuation[1]
                                name = mod_type
                        pygame.display.set_caption("Please input: {}{}{}{} and then press A.".format(name, punct, direction[self.get_keys[d]], mode_text))
                        if d in self.mask[mod_type]:
                            get_input(pad_cfg, button_map, axis_map, fb)
                            if stick_x or stick_y:
                                if mode:
                                    self.m_data[mod_type][d] = (stick_x, stick_y)
                                else:
                                    self.data[mod_type][d] = (stick_x,stick_y)
            get_directions()

            # This is where we will verify with the user that the data is correct or allow for re-entry of the data
            result = ctypes.windll.user32.MessageBoxA(0, "Keep the current values? No will redo the test.", "Calibration", 4)
            if result == IDYES:
                return
            else:
                run_test(mod_type, False)

        def run_calibration():
            result = ctypes.windll.user32.MessageBoxA(0, "First let's measure your unmodified Joystick inputs.", "Calibration", 0)
            if result == MB_OKCANCEL:
                run_test('Full', False)
                print 'Using values: {}'.format(self.data['Full'])

            result = ctypes.windll.user32.MessageBoxA(0, "Are you using Tilt 1?", "Calibration", 4)
            if result == IDYES:
                run_test('Tilt', False)
                print 'TILT values: {}'.format(self.data['Tilt'])
                print 'FULL values: {}'.format(self.data['Full'])
            else:
                self.mflags['Tilt'] = 0
                del self.data['Tilt']
                del self.m_data['Tilt']

            result = ctypes.windll.user32.MessageBoxA(0, "Are you using Tilt 2?", "Calibration", 4)
            if result == IDYES:
                run_test('Tilt2', False)
                print 'Using values: {}'.format(self.data['Tilt2'])
            else:
                self.mflags['Tilt2'] = 0
                del self.data['Tilt2']
                del self.m_data['Tilt2']

            result = ctypes.windll.user32.MessageBoxA(0, "Are you using Tilt 3?", "Calibration", 4)
            if result == IDYES:
                run_test('Tilt3', False)
                print 'Using values: {}'.format(self.data['Tilt3'])
            else:
                self.mflags['Tilt3'] = 0
                del self.data['Tilt3']
                del self.m_data['Tilt3']

            result = ctypes.windll.user32.MessageBoxA(0, "Are you using X1?", "Calibration", 4)
            if result == IDYES:
                run_test('X1', False)
                print 'Using values: {}'.format(self.data['X1'])
            else:
                self.mflags['X1'] = 0
                del self.data['X1']
                del self.m_data['X1']

            result = ctypes.windll.user32.MessageBoxA(0, "Are you using X2?", "Calibration", 4)
            if result == IDYES:
                run_test('X2', False)
                print 'Using values: {}'.format(self.data['X2'])
            else:
                self.mflags['X2'] = 0
                del self.data['X2']
                del self.m_data['X2']

            result = ctypes.windll.user32.MessageBoxA(0, "Are you using X3 (X1 + X2)?", "Calibration", 4)
            if result == IDYES:
                run_test('X3', False)
                print 'Using values: {}'.format(self.data['X3'])
            else:
                self.mflags['X3'] = 0
                del self.data['X3']
                del self.m_data['X3']

            result = ctypes.windll.user32.MessageBoxA(0, "Are you using Y1?", "Calibration", 4)
            if result == IDYES:
                run_test('Y1', False)
                print 'Using values: {}'.format(self.data['Y1'])
            else:
                self.mflags['Y1'] = 0
                del self.data['Y1']
                del self.m_data['Y1']

            result = ctypes.windll.user32.MessageBoxA(0, "Are you using Y2?", "Calibration", 4)
            if result == IDYES:
                run_test('Y2', False)
                print 'Using values: {}'.format(self.data['Y2'])
            else:
                self.mflags['Y2'] = 0
                del self.data['Y2']
                del self.m_data['Y2']

            result = ctypes.windll.user32.MessageBoxA(0, "Are you using Y3 (Y1 + Y2)?", "Calibration", 4)
            if result == IDYES:
                run_test('Y3', False)
                print 'Using values: {}'.format(self.data['Y3'])
            else:
                self.mflags['Y3'] = 0
                del self.data['Y3']
                del self.m_data['Y3']

        # Initializes the non-mode modifiers
        run_calibration()

        # Queries user for if the Mode button is being used
        result = ctypes.windll.user32.MessageBoxA(0, "Are you using Mode?", "Calibration", 4)
        if result == IDYES:
            for value in self.modifiers:
                if self.mflags[value]:
                    if value != 'Mode':
                        result = ctypes.windll.user32.MessageBoxA(0, "Input Mode + {}".format(value), "Calibration", 0)
                        run_test(value, True)
                        print 'Using values: {}'.format(self.m_data[value])
        else:
            self.m_data = {}
            self.mflags['Mode'] = 0

        # Data that is to be written out to file
        out_data = {'stick_data': self.data,
                    'mode_data': self.m_data,
                    'mflags': self.mflags,
                    'stick_mask': self.mask}
        # TODO MAKE THE EXTRA ELEMENT FOR MFLAGS LOAD PROPERLY AND MAKE IT LOAD THE MODE DATA AS WELL
        # Write JSON file
        with io.open(pad_cfg.path + '\stick_data.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(out_data,
                              indent=4,
                              separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))
        time.sleep(3)

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
        self.rect.center = self.position
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
        if value > 0.5:
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
        self.radius = int(radius)
        self.image_stick = image_stick
        self.image_free = image_free
        self.image_clear = image_clear
        self.directions = {'up': StickImage.Direction(self),
                           'down': StickImage.Direction(self),
                           'left': StickImage.Direction(self),
                           'right': StickImage.Direction(self),
                           'click': self}
        ButtonImage.__init__(self, screen, background, position, size,
                             image_stick, image_free, margin=self.radius,
                             copy_bg=True)

    def reset(self):
        for direction in self.directions.itervalues():
            direction.push(0)

    def get_xy(self):
        global stick_x
        global stick_y
        x = self.directions['right'].value - self.directions['left'].value
        y = self.directions['down'].value - self.directions['up'].value

        # Update and print that it was detected only when it has changed.
        if x and y:
            if x != stick_x or y != stick_y:
                stick_x = x
                stick_y = y
                print "Detected: ({},{})".format(x,y)


    def draw(self, force=False):
            if self.dirty or force:
                pass

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
        if self.value != value:
            if not silent:
                print "Shielding changed! Old: {}, New: {}".format(self.value, value)
            if value:
                if value < 1.0:
                    self.target.blit(self.image_push, self.position)
                    shield_buttons[0].push(1)
                    if not silent:
                        print ("LS + {} Detected!".format(self.name))
                else:
                    if self.value > 0:
                        pass
                        self.target.blit(self.image_push, self.position)
                        shield_buttons[0].push(0)
                        if not silent:
                            print "LS Released!"
                    else:
                        if not silent:
                            print ("Shielding with {}!".format(self.name))
                        self.target.blit(self.image_push, self.position)
                        shield_buttons[0].push(0)
            else:
                if not silent:
                    print "{} Trigger Released!".format(self.name)
                self.target.blit(self.image_free, self.position)
                shield_buttons[0].push(0)
            self.value = min(1, max(0, value))


    def update_redraws(self):
        assert isinstance(self, TriggerImage)
        self.value = .5
        self.draw(True)
        self.push(0, True)

    def draw(self, force=False):
        if self.dirty or force:
            ButtonImage.draw(self)
            for b in self.redraws:
                b.draw(force=True)


class PadImage:
    def __init__(self, cfg, screen):
        global shield_buttons
        image_clear = None
        assert isinstance(cfg, configurator.PadConfig)
        self.buttons = dict()
        self.triggers = dict()
        self.sticks = dict()

        def load_image(name):
            return pygame.image.load(os.path.join(cfg.path, '%s.png' % name))

        self.target = screen
        self.target.fill(cfg.background_color)
        self.background = load_image(cfg.background)
        self.target.blit(self.background, (0, 0))
        self.path = cfg.path

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
            if visualizer.get_button_index.has_key(button_cfg.name):
                index = visualizer.get_button_index[button_cfg.name]
                if index == 13:
                    index = visualizer.get_shield_index[button_cfg.name]
                    shield_buttons[index] = obj
                elif index:
                    visualizer.button_obj[index] = obj
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
        for trigger in self.triggers.itervalues():
            trigger.update_redraws()


    def draw(self):
        for button in self.buttons.itervalues():
            assert isinstance(button, ButtonImage)
            button.draw()
        for stick in self.sticks.itervalues():
            assert isinstance(stick, StickImage)
            stick.get_xy()
            stick.draw()
        for trigger in self.triggers.itervalues():
            assert isinstance(trigger, TriggerImage)
            trigger.draw()


def _get_target(pad_gfx, map_element):
    elt_type = map_element['type']
    elt_name = map_element['name']
    target = None
    if elt_type == 'button':
        target = pad_gfx.buttons[elt_name]
    elif elt_type == 'trigger':
        target = pad_gfx.triggers[elt_name]
    elif elt_type == 'stick':
        which = map_element['direction']
        target = pad_gfx.sticks[elt_name].directions[which]
    assert target is not None
    return target


def get_input(pad_gfx, button_map, axis_map, fb):
    polled = False
    while not polled:
        pygame.event.peek(pygame.QUIT)
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if str(event.button) in button_map:
                    elt = button_map[str(event.button)]
                    _get_target(pad_gfx, elt).push(1)
                    polled = True
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
            else:
                pass
            fb.handle_event(event)
        pad_gfx.draw()
        fb.flip()
        fb.limit_fps(set_caption=False)


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
    pad_gfx.draw()
    fb.flip()
    fb.limit_fps(set_caption=False)
    test_obj = CalibrationTests()
    test_obj.init_tests(pad_gfx, button_map, axis_map, fb)

if __name__ == '__main__':
    main('smashbox', 0)


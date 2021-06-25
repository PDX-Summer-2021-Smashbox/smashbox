import math
import pygame
#import pymouse
import os
import json

import configurator
import frame_buffer
import visualizer
import util
import ctypes

map_path = None

# Modified mapping functions used to map buttons to locations. Default gamecube controller inputs are assumed.
class PadMapper:
    def __init__(self, skin, joy_index):
        self.cfg = configurator.PadConfig(skin)
        self.js = pygame.joystick.Joystick(joy_index)
        self.js.init()
        self.fb = frame_buffer.FrameBuffer(
            self.cfg.size, self.cfg.size, scale_smooth=self.cfg.anti_aliasing,
            background_color=self.cfg.background_color)

        # Draws a smashbox with no button assignments
        self.gfx = visualizer.EmptyPadImage(self.cfg, self.fb)

        # Create the objects used to populate the custom skin.json
        self.general = {"background": "base", "background-color": [16, 20, 24], "size": [1219, 624], "anti-aliasing": True}
        self.sticks = {"control-stick":{"position": [352, 218], "size": [72, 72], "radius": 360}}
        self.triggers = {}
        self.buttons = {}

    @staticmethod
    def display_message(msg):
        print msg
        pygame.display.set_caption(msg)

    # This function manually maps all buttons and then creates the objects similarly to get all mappings.
    # The whole goal is to simply build the custom skin.json file since the map.json is basically just a standard
    # Gamecube controller mapping, it shouldn't need to vary when using smashbox specifically.
    def map_all_buttons(self):
        new_config = util.recursive_default_dict()
        data = new_config[self.js.get_name()]
        self.fb.flip(delay=True)
        final_result = None

        # Windows prompt and button types
        MB_OK = 0
        MB_OKCANCEL = 1
        MB_YESNOCANCEL = 3
        MB_YESNO = 4
        IDOK = 0
        IDCANCEL = 2
        IDABORT = 3
        IDYES = 6
        IDNO = 7

        # We need to pass a name, a position, and a size

        analog_buttons = ["Up", "Down", "Left", "Right"]
        cstick_buttons = ["C-Up", "C-Down", "C-Left", "C-Right"]
        dpad_buttons = ["DPad-Up", "DPad-Down", "DPad-Left", "DPad-Right"]
        normal_buttons = ["A", "B", "X", "Y", "Z", "Start"]
        trigger_buttons = ["L", "R", "Shield-Toggle", "1BLS"]
        modifier_buttons = ["X1", "X2", "X3", "Y1", "Y2", "Y3", "Tilt", "Tilt2", "Tilt3", "Mode", "Mirror", "Flip", "Invert"]

        map_order = [analog_buttons, cstick_buttons, dpad_buttons, normal_buttons, trigger_buttons, modifier_buttons]

        result = ctypes.windll.user32.MessageBoxA(0, "Let's map your buttons! \n\nPay attention to the window title in "
                                                     "the top left corner, and click on the requested button to map it."
                                                   , "Button-Mapper", 0)
        if result == MB_OKCANCEL:
            pass

        # First ask if we have duplicate buttons to map. Also brief them that this may be glitchy or not know which
        # button to default to when pressed because the input is ambiguous. This is mainly just for drawing it right.
        result = ctypes.windll.user32.MessageBoxA(0, "Does your layout contain duplicate buttons?", "Mapper", 4)
        if result == IDYES:
            duplicate_buttons = True
        else:
            duplicate_buttons = False

        def is_button_being_used(button):
            result = ctypes.windll.user32.MessageBoxA(0, "Are you mapping a button for {}?".format(button), "Mapper", 4)
            if result == IDYES:
                return True
            else:
                return False

        def are_there_more_duplicates():
            result = ctypes.windll.user32.MessageBoxA(0, "Do you have another duplicate of this button to map?".format(button), "Mapper", 4)
            if result == IDYES:
                return True
            else:
                return False

        def get_mouse_click_position():
            final_result = None
            button_coordinates = { 'UL-1':['',(361, 136)], 'UL-2':['',(270, 210)], 'UL-3':['',(352, 218)],
                                   'UL-4':['',(434, 227)], 'UL-5':['',(195, 253)], 'C-1':['',(611, 91)],
                                   'BL-1':['',(435, 378)], 'BL-2':['',(517, 378)], 'BL-3':['',(476, 449)],
                                   'BL-4':['',(558, 449)], 'BR-1':['',(706, 378)], 'BR-2':['',(789, 378)],
                                   'BR-3':['',(664, 449)], 'BR-4':['',(747, 449)], 'BR-5':['',(706, 520)],
                                   'UR-1':['',(797, 184)], 'UR-2':['',(863, 136)], 'UR-3':['',(945, 139)],
                                   'UR-4':['',(1020, 172)], 'UR-5':['',(804, 266)], 'UR-6':['',(871, 218)],
                                   'UR-7':['',(953, 221)], 'UR-8':['',(1029, 254)] }
            pygame.event.pump()
            while final_result is None:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.MOUSEBUTTONUP:
                        mouse_coords = pygame.mouse.get_pos()
                        mouse_x = mouse_coords[0]
                        mouse_y = mouse_coords[1]
                        for button in button_coordinates.iteritems():
                            button_x = button[1][1][0]
                            button_y = button[1][1][1]
                            if math.sqrt((mouse_x-button_x)**2 + (mouse_y-button_y)**2)<36:
                                print 'You clicked on button {}'.format(button[0])
                                position = button_coordinates[button[0]][1]
                                return position
                                #break
            #return final_result
            return None

        def get_button_location(button):
            pygame.display.set_caption("Please click on the button for: {}.".format(button))
            position = get_mouse_click_position()
            name = button
            size = [72, 72]
            depth = 55

            # L and R are trigger type, the rest are all button type
            if button == "L" or button == "R":
                self.triggers[name] = {"position": [position[0],position[1]],
                                       "size":size,
                                       "depth": depth}
                button_type = "trigger"
            else:
                # Perform necessary renaming to match resource names... I should probably clean this up...
                if name == "1BLS":
                    name = "LS"
                elif name == "shield-toggle":
                    name = "ST"
                elif name == "Mode":
                    name = "M"
                elif name == "Tilt":
                    name = "T"
                elif name == "Tilt2":
                    name = "T2"
                elif name == "Left" or name == "Right" or name == "Up" or name == "Down":
                    name = name.lower()

                # Update the data by storing the data into the index for that button
                self.buttons[name] = {"position": [position[0],position[1]],
                                       "size":size}
            print "Added {} to position {}".format(name, position)

        # Map all controller buttons in order
        for button_type in map_order:
            for button in button_type:
                if is_button_being_used(button):
                    if not duplicate_buttons:
                        more_duplicates = False
                    else:
                        more_duplicates = True
                    while 1:
                        new_button = get_button_location(button)
                        if more_duplicates:
                            more_duplicates = are_there_more_duplicates()
                        if not more_duplicates:
                            break

        # Done iterating through all buttons! Export the data to the skin.json file!
        global map_path
        path = map_path
        if not os.path.exists(path):
            os.makedirs(path)
        map_filename = os.path.join(path, 'skin.json')
        with open(map_filename, 'w') as f:
            data = {"general": self.general,
                    "triggers": self.triggers,
                    "sticks": self.sticks,
                    "buttons": self.buttons
                    }
            json.dump(data, f, indent=2, sort_keys=True)

        # Export the flags representing which buttons have been mapped so we can tell to highlight 1 + 2 or 3.
        data.clear()
        for i in self.buttons:
            if i == "Tilt3" or i == "X3" or i == "Y3":
                data[i] = True

        map_filename = os.path.join(path, 'flags.json')
        with open(map_filename, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)


def main(skin, joy_index):
    global  map_path
    map_path = configurator.get_map_path(skin)
    all_maps = configurator.load_mappings(skin)
    pygame.display.init()
    pygame.joystick.init()
    new_map = PadMapper(skin, joy_index).map_all_buttons()
    all_maps.update(new_map)

if __name__ == '__main__':
    main('smashbox', 0)

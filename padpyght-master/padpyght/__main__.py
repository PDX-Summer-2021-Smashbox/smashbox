# An open source gamepad visualizer inspired by PadLight.
# By Darren 'lifning' Alton

import os
import pkg_resources
import sys

import pygame

import configurator
import mapper
import smapper      # Visual mapping utility for smashbox
import calibration
import visualizer


def main(skin, joy_index):
    pygame.display.init()
    pygame.joystick.init()

    joy = pygame.joystick.Joystick(joy_index)
    joy.init()
    mappings = configurator.load_mappings(skin)
    if joy.get_name() not in mappings:
       smapper.main(skin, joy_index)
       #mapper.main(skin, joy_index) #TODO UNCOMMENT THIS TO UNDO
    visualizer.main(skin, joy_index)

joy_index = 0

try:
    if len(sys.argv) > 1:
        # HACK, since fallback for not having pgu is console mode, we can just
        # raise ImportError to simulate not having pgu.
        raise ImportError
    import pgu.gui
except ImportError:
    pgu = None
    if len(sys.argv) > 1:
        _skin = sys.argv[1]
    if len(sys.argv) > 2:
        joy_index = int(sys.argv[2])
    main(_skin, joy_index)
    sys.exit()

app = pgu.gui.Desktop()
app.connect(pgu.gui.QUIT, app.quit, None)
box = pgu.gui.Container(width=644, height=446)
joy_list = pgu.gui.List(width=644, height=110)
skin_list = pgu.gui.List(width=644, height=110)
remap_btn = pgu.gui.Button('map', width=200, height=40)
calibrate_btn = pgu.gui.Button('calibrate', width=200, height=40)
run_btn = pgu.gui.Button('start', width=200, height=40)
joy_label = pgu.gui.TextArea('Input Devices: ', width=640, height=20)
skin_label = pgu.gui.TextArea('Smashbox Profiles: ', width=640, height=20)
help = pgu.gui.TextArea('Select your input device and profile. Map and then calibrate your keys if you haven\'t yet. '
                        'Press "start" to fire up the stream overlay.\n\nNote: This program remembers the last input '
                        'device and profile used. If the options haven\'t changed just press "start".'
                        , width=636, height=100)
joy_label.background = False
joy_label.focusable = False
skin_label.background = False
skin_label.focusable = False
help.disabled = True
joy_label.disabled = True
skin_label.disabled = True
box.add(joy_label, 4, 0)
box.add(joy_list, 4, 22)
box.add(skin_label, 4, 150)
box.add(skin_list, 4, 172)
box.add(help, 4, 290)
box.add(run_btn, 438, 400)
box.add(remap_btn, 2, 400)
box.add(calibrate_btn, 220, 400)


pygame.joystick.init()
for i in xrange(pygame.joystick.get_count()):
    name = pygame.joystick.Joystick(i).get_name()
    joy_list.add('{}: {}'.format(i, name), value=i)


def get_profile_path(skin):
    base_dir = pkg_resources.resource_filename('padpyght', 'skins')
    path = os.path.join(base_dir, skin.lstrip())
    return path

def list_skin_paths():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.join(sys._MEIPASS, 'padpyght', 'skins')
        for dir_name in os.listdir(base_dir):
            path = os.path.join(base_dir, dir_name)
            yield dir_name, path
    else:
        for dir_name in pkg_resources.resource_listdir('padpyght', 'skins'):
            path = pkg_resources.resource_filename('padpyght',
                                                   'skins/%s' % dir_name)
            yield dir_name, path

for dir_name, path in list_skin_paths():
    cfg = os.path.join(path, 'skin.json')
    if os.path.exists(cfg):
        skin_list.add(dir_name, value=dir_name)
    else:
        print 'skin.json missing from', path


def load_last_joy():
    if joy_list.value is not None:
        return
    path = os.path.dirname(__file__)
    joy_cfg = os.path.relpath(path + '\default_joy.ini')
    if os.path.exists(joy_cfg):
        joy_cfg = open(path + '\default_joy.ini', 'r')
        input = joy_cfg.readline()
        input = input.split(',')[1]
        joy_list.value = input
        joy_cfg.close()
    else:
        save_last_joy()
    return joy_list.value


def save_last_joy():
    path = os.path.dirname(__file__)
    joy_cfg = open(path + '\default_joy.ini', 'w')
    joy_cfg.write("joy_last , {}".format(joy_list.value))
    joy_cfg.close()


def load_last_skin():
    if skin_list.value is not None:
        return
    path = os.path.dirname(__file__)
    skin_cfg = os.path.relpath(path + '\default_skin.ini')
    if os.path.exists(skin_cfg):
        skin_cfg = open(path + '\default_skin.ini', 'r')
        input = skin_cfg.readline()
        input = input.split(',')[1]
        skin_list.value = input
        skin_cfg.close()
    else:
        save_last_skin()
    return skin_list.value


def save_last_skin():
    path = os.path.dirname(__file__)
    skin_cfg = open(path + '\default_skin.ini', 'w')
    skin_cfg.write("skin_last , {}".format(skin_list.value))
    skin_cfg.close()


def main_wrapper():
    if skin_list.value is not None and joy_list.value is not None:
        save_last_joy()
        save_last_skin()
        screen = pygame.display.get_surface()
        size, flags = screen.get_size(), screen.get_flags()
        main(skin_list.value, int(joy_list.value))
        pygame.display.set_mode(size, flags)
        app.repaint()


def remap_wrapper():
    if skin_list.value is not None and joy_list.value is not None:
        save_last_joy()
        screen = pygame.display.get_surface()
        size, flags = screen.get_size(), screen.get_flags()
        smapper.main(skin_list.value, int(joy_list.value))
        # mapper.main(skin_list.value, int(joy_list.value)) TODO: UNCOMMENT THIS TO UNDO
        pygame.display.set_mode(size, flags)
        app.repaint()

def calibrate_wrapper():
    if skin_list.value is not None and joy_list.value is not None:
        save_last_joy()
        screen = pygame.display.get_surface()
        size, flags = screen.get_size(), screen.get_flags()
        calibration.main(skin_list.value, int(joy_list.value))
        pygame.display.set_mode(size, flags)
        app.repaint()

load_last_joy()
load_last_skin()

configurator.get_map_path(skin_list.value)
run_btn.connect(pgu.gui.CLICK, main_wrapper)
remap_btn.connect(pgu.gui.CLICK, remap_wrapper)
calibrate_btn.connect(pgu.gui.CLICK, calibrate_wrapper)
box.repaint()
app.run(box)

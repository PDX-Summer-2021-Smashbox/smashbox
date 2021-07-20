from smashbox_viewer import button_roles
from smashbox_viewer.button_roles import BUTTON_ROLES
from smashbox_viewer.button_locations import BUTTON_NAMES

class Mapper:
    '''
    Class to map the buttons to their roles.
    Two options to use this class; 1) CLI
                                   2) GUI

    The cli will return the mapped button dictionary

    TODO  GUI client                             
    '''
    def __init__(self):
        self.mapped_buttons = {}

    
    def cli(self):
        # Print the button roles for the user
        print("INDEX    BUTTON ROLE")
        for indx, role in enumerate(BUTTON_ROLES):
            print("{0}    |  {1}".format(indx, role))
        # Map the buttons    
        for button in BUTTON_NAMES:
            map_index = -1
            while not int(map_index) in range(len(BUTTON_ROLES)):
                map_index = input("Set {0} to index: ".format(button))
            self.mapped_buttons[button] = BUTTON_ROLES[int(map_index)]
        
        return self.mapped_buttons

    
    def gui(self):
        pass





# Testing

def main():
    test_mapper = Mapper()
    mapped_roles = test_mapper.cli()

    print(mapped_roles)

if __name__ == "__main__":
    main()


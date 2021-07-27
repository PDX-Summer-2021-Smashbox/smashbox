<<<<<<< Updated upstream
from smashbox_viewer import button_roles
=======
>>>>>>> Stashed changes
from smashbox_viewer.button_roles import BUTTON_ROLES
from smashbox_viewer.button_locations import BUTTON_NAMES

class Mapper:
    '''
    Class to map the buttons to their roles.
    Two options to use this class; 1) CLI
                                   2) GUI

    The cli will return the mapped button dictionary

<<<<<<< Updated upstream
    TODO  GUI client                             
=======
    TODO
        Clean up code a bit  
        GUI client                             
>>>>>>> Stashed changes
    '''
    def __init__(self):
        self.mapped_buttons = {}

<<<<<<< Updated upstream
    
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
=======
    def verify_input(self, button):
        map_index = -1
        while not int(map_index) in range(len(BUTTON_ROLES)):
            index = input("Set {0} to index: ".format(button))
            map_index = index if index.isdigit() else -1

        return int(map_index)

    
    def cli(self):
        print("INDEX    BUTTON ROLE")
        for indx, role in enumerate(BUTTON_ROLES):
            print("{0}    |  {1}".format(indx, role))
        # Loop thru each button and map to a role    
        for button in BUTTON_NAMES:
            map_index = self.verify_input(button)

            self.mapped_buttons[button] = BUTTON_ROLES[map_index]
>>>>>>> Stashed changes
        
        return self.mapped_buttons

    
    def gui(self):
        pass





<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
# Testing

def main():
    test_mapper = Mapper()
    mapped_roles = test_mapper.cli()

    print(mapped_roles)

if __name__ == "__main__":
    main()


"""
 TOTAL BUTTON COUNT: 26 Buttons
 GROUP NAMES: Enumerates each of the groups of buttons on controller.
 BUTTON NAMES: Enumerates each of the names for each button on the controller.
 GROUP SIZES: Dictionary containing the total number of buttons in each group.
 BUTTON GROUPS: Dictionary where keys are group names and entries are lists of button names specific to that group.
 BUTTON LOCATIONS: Dictionary where keys are button names and entries are X,Y tuple center coordinates for a button.
"""

TOTAL_BUTTON_COUNT = 26

GROUP_NAMES = [
    "Top_Left",
    "Bottom_Left",
    "Top_Center",
    "Top_Right",
    "Bottom_Right",
    "Left_Side"  # Rocker switch and Nunchuk button assignments.
]

BUTTON_NAMES = [
    # Contains the following button names: Button_1, Button_2, ... BUTTON_TOTAL_BUTTON_COUNT.
    'Button_' + str(x) for x in range(1,TOTAL_BUTTON_COUNT + 1)
]

# Number of buttons in each group.
GROUP_SIZES = {
    GROUP_NAMES[0]: 5,  # Top Left (1-5)
    GROUP_NAMES[1]: 4,  # Bottom Left (6-9)
    GROUP_NAMES[2]: 1,  # Top Center (10)
    GROUP_NAMES[3]: 8,  # Top Right (11-18)
    GROUP_NAMES[4]: 5,  # Bottom Right (19-23)
    GROUP_NAMES[5]: 3,  # Left Side (24-26)
}

# Specific buttons assigned to each group.
BUTTON_GROUPS = {
    GROUP_NAMES[0]: (BUTTON_NAMES[0:5]),
    GROUP_NAMES[1]: (BUTTON_NAMES[5:9]),
    GROUP_NAMES[2]: (BUTTON_NAMES[9]),
    GROUP_NAMES[3]: (BUTTON_NAMES[10:18]),
    GROUP_NAMES[4]: (BUTTON_NAMES[18:23]),
    GROUP_NAMES[5]: (BUTTON_NAMES[23:])
}

# Specific tuple assignments representing the default X,Y button coordinates for each button.
# a JSON type configuration file can probably be provided that's skin-specific however these are the defaults.
BUTTON_LOCATIONS = {
    "Button_1": (361, 136),
    "Button_2": (195, 253),
    "Button_3": (270, 210),
    "Button_4": (352, 218),
    "Button_5": (434, 227),
    "Button_6": (435, 378),
    "Button_7": (517, 378),
    "Button_8": (476, 449),
    "Button_9": (558, 449),
    "Button_10": (611, 91),
    "Button_11": (795, 184),
    "Button_12": (863, 136),
    "Button_13": (945, 139),
    "Button_14": (1020, 172),
    "Button_15": (804, 266),
    "Button_16": (871, 218),
    "Button_17": (953, 221),
    "Button_18": (1029, 254),
    "Button_19": (706, 378),
    "Button_20": (789, 378),
    "Button_21": (664, 449),
    "Button_22": (747, 449),
    "Button_23": (706, 520),
    "Button_24": (0, 41),     # Left Side Rocker Toggle in Top Left
    "Button_25": (976, 492),  # Right Nunchuk Top button display in Bottom Right
    "Button_26": (976, 570),  # Right Nunchuk Bottom button display in Bottom Right
}

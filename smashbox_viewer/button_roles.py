BUTTON_ROLES = [
    """
        Enumerates each of the roles that are assignable to individual buttons on a Smash Box controller.
    """
    "Button_Disabled",  # Disables the button for this particular profile
    # Joystick Inputs (Range from +/- 0.0 to +/- 1.0 in increments of 1/127).
    "Analog_Stick_Up",  # Ranges from 0.0 to  1.0
    "Analog_Stick_Down",  # Ranges from 0.0 to -1.0
    "Analog_Stick_Left",  # Ranges from 0.0 to -1.0
    "Analog_Stick_Right",  # Ranges from 0.0 to  1.0
    "C_Stick_Up",  # Ranges from 0.0 to  1.0
    "C_Stick_Down",  # Ranges from 0.0 to -1.0
    "C_Stick_Left",  # Ranges from 0.0 to -1.0
    "C_Stick_Right",  # Ranges from 0.0 to  1.0
    "C_Stick_Down_Right",  # Ranges from (0.0, 0.0) to (1.0, -1.0) the actual value can be modified through modifying
    # the default C-Stick range values, as well as the alternate values accessed through Mode.
    # Normal Button Inputs
    "Button_DPad_Up",  # Presses Up on the Directional Pad.
    "Button_DPad_Down",  # Presses Down on the Directional Pad.
    "Button_DPad_Left",  # Presses Left on the Directional Pad.
    "Button_DPad_Right",  # Presses Right on the Directional Pad.
    "Button_A",  # Presses the A button.
    "Button_B",  # Presses the B button.
    "Button_X",  # Presses the X button.
    "Button_Y",  # Presses the Y button.
    "Button_Z",  # Presses the Z button.
    "Button_Start",  # Presses the Start button.
    # Normal Trigger Inputs
    "Trigger_L",  # Digital button press normally actuated through full L trigger depression.
    "Trigger_R",  # Digital button press normally actuated through full R trigger depression.
    "Trigger_Light_L",  # Analog button press ranging from 0.0 to 1.0 with 256 values in increments of 0.007143.
    "Trigger_Light_R",  # Analog button press ranging from 0.0 to 1.0 with 256 values in increments of 0.007143.
    # Since the increment is approximately 1/140, values are limited to a maximum of 1.0.
    # Modifier Button Inputs used for modifying the Analog Stick
    "Modifier_X_1",  # Modifies the horizontal axis, with priority over Tilt X-axis components.
    "Modifier_X_2",  # Modifies the horizontal axis, with priority over Tilt X-axis components, and X_1.
    "Modifier_X_3",  # Modifies the horizontal axis, with priority over Tilt X-axis components, X_1, X_2.
    # X_3 values can also be accessed through combining X_1 and X_2 button inputs.
    "Modifier_Y_1",  # Modifies the vertical axis, with priority over Tilt Y-axis components.
    "Modifier_Y_2",  # Modifies the vertical axis, with priority over Tilt Y-axis components, Y_1.
    "Modifier_Y_3",  # Modifies the vertical axis, with priority over Tilt Y-axis components, Y_1, Y_2.
    # Y_3 values can also be accessed through combining Y_1 and Y_2 button inputs.
    "Modifier_Tilt",  # Modifies both Analog Stick axes.
    "Modifier_Tilt_2",  # Modifies both Analog Stick axes, with priority over Tilt.
    "Modifier_Tilt_3",  # Modifies both Analog Stick axes, with priority over Tilt2.
    # Tilt_3 values can also be accessed through combining Tilt and Tilt_2 button inputs.
    # Advanced Joystick and Trigger Modifiers
    "Modifier_Shield_Toggle",  # Toggles Digital L/R to Analog, and Light L/R to Digital.
    "Modifier_Mode",  # Accesses alternate values for unmodified Analog Stick and C Stick ranges,
    # as well as alternate X/Y and Tilt modifier values.
    # Additional Modifiers with varying properties (unnecessary for MVP)
    "Modifier_Mode_With_C_Stick_Rotate",  # Same as Mode but also rotates the C-Stick (TODO: get details for this)
    "Modifier_Mode_With_Shield_Toggle",  # Same as Mode but also toggles between Light and Hard shield.
    "Modifier_Mode_With_Shield_Toggle_With_C_Stick_Rotate",  # Same as Mode with Shield Toggle but Rotates C Stick.
    "Modifier_C_Stick_Rotate",  # Rotates the C Stick (TODO: get details for this)
    "Modifier_DPad_Toggle",  # X1 becomes DPad_Left, Y1 becomes DPad_Up,
    # X2 becomes DPad_Down, Y2 becomes DPad_Right
    "Modifier_Analog_Stick_Becomes_C_Stick",  # Analog Stick directions become C-Stick directional Inputs.
    "Modifier_Analog_Stick_Becomes_Dpad",  # Analog Stick directions become Dpad directional inputs.
    # Extra buttons specific to PC-USB mode for mapping buttons like PS4 home button, back button, etc.
    "USB_EXTRA_1",
    "USB_EXTRA_2",
    "USB_EXTRA_3",
    "USB_EXTRA_4",
    "USB_EXTRA_5",
    "USB_EXTRA_6",
]

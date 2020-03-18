import enum

class EmailTemplates(enum.Enum):
    welcomeMessage = ""
    sendResetURL = """Hi {}, \nYou have requested to reset your password. Click the link below to reset it.\n\n{}\n\nIf you did not request a password reset, please ignore this email or reply to let us know. This password is only valid for the next 15 minutes."""
    updatedPassword = """Hi {}, \nYou have recently changed your password. If the
    change was done by you then you can ignore this mail. \nHowever if it wasn't you
    please get in touch with us as soon as possible"""
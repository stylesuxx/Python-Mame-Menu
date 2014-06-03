"Holds information about a game"
class Game:
    slug = None
    name = None
    description = None
    manufacturer = None
    year = None
    cloneof = None
    state = 'unknown'
    played = 0
    time = 0

    def __init__(self):
        "Constructor"

    def __del__(self):
        "Destructor"
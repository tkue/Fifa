

from Fifa18.Config import FifaConfig
from Fifa18.Database import FifaDatabase


from enum import Enum

class Player(object):
    def __int__(self, player_id: int, database: FifaDatabase):
        self.player_id = player_id
        self.database = database



class FormationType(Enum):
    Formation_442 = '4-4-2'


class Formation(object):
    def __init__(self, formation_type: FormationType):
        self.formation_type = formation_type


class Formation442(Formation):
    def __init__(self):
        super(Formation442, self).__init__(FormationType.Formation_442)



if __name__ == '__main__':
    config = FifaConfig('config.json')
    db = FifaDatabase(config)

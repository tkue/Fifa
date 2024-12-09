import urllib

from WebScraping.GetData.Player import Player
from bs4 import BeautifulSoup


class FutBinPlayer(Player):
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def get_url(self):
        try:
            return urllib.parse.urljoin('https://www.futbin.com/18/player', self.soup.attrs['data-url'])
        except:
            return None

    def get_name(self):
        try:
            return self.soup.find(class_='player_name_players_table').text
        except:
            return None

    def get_club(self):
        try:
            return self.soup.find('span', class_='players_club_nation').findAll('a')[0].attrs['data-original-title']
        except:
            return None

    def get_country(self):
        try:
            return self.soup.find('span', class_='players_club_nation').findAll('a')[1].attrs['data-original-title']
        except:
            return None

    def get_league(self):
        try:
            return self.soup.find('span', class_='players_club_nation').findAll('a')[2].attrs['data-original-title']
        except:
            return None

    def get_overall_rating(self):
        try:
            return int(self.soup.findAll('td')[1].text)
        except:
            return None

    def get_position(self):
        try:
            return self.soup.findAll('td')[2].text
        except:
            return None

    def get_edition(self):
        try:
            return self.soup.findAll('td')[3].text
        except:
            return None

    # TODO: Parse costs (e.g. 4.8K)
    def get_cost_playstation(self):
        try:
            return Player.parse_cost(self.soup.findAll('td')[4].text)
        except:
            return None

    def get_cost_xbox(self):
        try:
            return Player.parse_cost(self.soup.findAll('td')[5].text)
        except:
            return None

    def get_cost_pc(self):
        try:
            return Player.parse_cost(self.soup.findAll('td')[6].text)
        except:
            return None

    def get_skill_moves(self):
        try:
            return int(self.soup.findAll('td')[7].text)
        except:
            return None

    def get_weak_foot(self):
        try:
            return int(self.soup.findAll('td')[8].text)
        except:
            return None

    def get_attacking_work_rate(self):
        try:
            return self.soup.findAll('td')[9].text.split('\\')[0].strip()
        except:
            return None

    def get_defensive_work_rate(self):
        try:
            return self.soup.findAll('td')[9].text.split('\\')[1].strip()
        except:
            return None

    def get_pace(self):
        try:
            return int(self.soup.findAll('td')[10].text)
        except:
            return None

    def get_shooting(self):
        try:
            return int(self.soup.findAll('td')[11].text)
        except:
            return None

    def get_passing(self):
        try:
            return int(self.soup.findAll('td')[12].text)
        except:
            return None

    def get_dribbling(self):
        try:
            return int(self.soup.findAll('td')[13].text)
        except:
            return None

    def get_defense(self):
        try:
            return int(self.soup.findAll('td')[14].text)
        except:
            return None

    def get_physical(self):
        try:
            return int(self.soup.findAll('td')[15].text)
        except:
            return None

    def get_height_cm(self):
        try:
            return self.soup.findAll('td')[16].text.split('|')[0].strip()
        except:
            return None

    def get_height_ft(self):
        try:
            return self.soup.findAll('td')[16].text.split('|')[1]
        except:
            return None

    def get_popularity(self):
        try:
            return self.soup.findAll('td')[17].text
        except:
            return None

    def get_base_stats(self):
        try:
            return self.soup.findAll('td')[18].text
        except:
            return None

    def get_in_game_stats(self):
        try:
            return self.soup.findAll('td')[19].text
        except:
            return None

    def get_height_inches(self):
        try:
            return int(Player.parse_height_to_get_inches(self.get_height_ft()))
        except:
            return None

import sqlite3
import urllib

from bs4 import BeautifulSoup

from WebScraping.GetData.FutBin.FutBinPlayer import FutBinPlayer
from WebScraping.GetData.SiteType import SiteType

from WebScraping.GetData.ISession import ISession

import requests


class FutBinSession(ISession):
    def __init__(self, config_path: str):

        super(FutBinSession, self).__init__(config_path, SiteType.FUTBIN)

    def __get_urls(self):
        """
        FutBin doesn't give us all players from one start URL, so we have to get them in sections
        Players end when the page gets past 99

        Returns URLs like:
            https://www.futbin.com/18/players?page=90&player_rating=40-50
            https://www.futbin.com/18/players?page=90&player_rating=50-60

        All the way until end rating of 99

        Must start at 40
        """
        start_url = self.get_start_url()

        start_rating = 40
        end_rating = 99

        urls = []

        max_rating = start_rating + 10
        min_rating = start_rating

        while max_rating <= end_rating:
            url = start_url + '&player_rating={0}-{1}'.format(min_rating, max_rating)

            urls.append(url)

            if max_rating == 90:
                max_rating += 9
            else:
                max_rating += 10

            min_rating += 10

        return urls


    def begin_processing_urls(self, url: str):
        self.logger.info('Processing URL: {0}'.format(url))

        soup = self.get_soup_from_page(url)
        self.process_page(soup)

        next_button_url = self.get_next_button_url(soup)

        if not next_button_url:
            self.end_session()
            return

        # Next page
        is_has_next_button = False
        if next_button_url:
            is_has_next_button = True

        while is_has_next_button:
            soup = self.get_soup_from_page(next_button_url)
            self.process_page(soup)

            next_button_url = self.get_next_button_url(soup)

            if not next_button_url:
                is_has_next_button = False
            else:
                is_has_next_button = True

    def start_session(self):
        self.check_if_can_continue()
        for url in self.__get_urls()    :
            self.begin_processing_urls(url)


    def end_session(self):
        self.logger.info('Done web scraping')

    def get_next_button_url(self, soup: BeautifulSoup):
        if not soup:
            return

        try:
            # rel_url = soup.find('a', class_='pagination_a').attrs['href']

            # rel_url = soup.find('a', id='next').attrs['href']
            rel_url = None
            buttons = soup.findAll('a', class_='pagination_a')
            for button in buttons:
                if button.attrs['id'] == 'next':
                    rel_url = button.attrs['href']

            if not rel_url:
                return None

            return urllib.parse.urljoin(self.get_site_base_url(), rel_url)
        except:
            return None

    def process_page(self, soup: BeautifulSoup):
        if not soup:
            return

        # self.check_if_can_continue()

        players = self.get_players_from_page(soup)
        self.insert_players_into_database(players)

    def get_soup_from_page(self, url: str):
        if not url:
            return

        self.logger.info('Getting BeautifulSoup for URL: {0}'.format(url))

        r = requests.get(url)
        return BeautifulSoup(r.text, 'html.parser')

    def get_players_from_page(self, soup: BeautifulSoup):
        if not soup:
            return

        # TODO: Broke here when it couldn't find the table. Maybe wasn't able to get the webpage?
        try:
            results = soup.find('table', class_='table table-striped table-hover').findAll('tr')
        except AttributeError as ae:
            self.logger.warning('No table to get data from\n{}'.format(ae))
            return

        if not results:
            self.logger.warning('Results table is null. Unable to get players')
            return

        players = []

        for result in results:
            player = FutBinPlayer(result)
            players.append(player)

            # player = {
            #     'url': urllib.parse.urljoin('https://www.futbin.com/18/player', result.attrs['data-url']),
            #     'name': result.find(class_='player_name_players_table').text,
            #     'club': result.find('span', class_='players_club_nation').findAll('a')[0].attrs['data-original-title'],
            #     'country': result.find('span', class_='players_club_nation').findAll('a')[1].attrs['data-original-title'],
            #     'league': result.find('span', class_='players_club_nation').findAll('a')[2].attrs['data-original-title'],
            #     'overall_rating': result.findAll('td')[1].text,
            #     'position': result.findAll('td')[2].text,
            #     'edition': result.findAll('td')[3].text,
            #     'cost_playstation': result.findAll('td')[4].text,
            #     'cost_xbox': result.findAll('td')[5].text,
            #     'cost_pc': result.findAll('td')[6].text,
            #     'skill_moves': result.findAll('td')[7].text,
            #     'weak_foot': result.findAll('td')[8].text,
            #     'attacking_work_rate': result.findAll('td')[9].text.split('\\')[0].strip(),
            #     'defensive_work_rate': result.findAll('td')[9].text.split('\\')[1].strip(),
            #     'passing': result.findAll('td')[10].text,
            #     'shooting': result.findAll('td')[11].text,
            #     'passing': result.findAll('td')[12].text,
            #     'dribbling': result.findAll('td')[13].text,
            #     'defense': result.findAll('td')[14].text,
            #     'physical': result.findAll('td')[15].text,
            #     'height_cm': result.findAll('td')[16].text.split('|')[0].strip(),
            #     'height_ft': result.findAll('td')[16].text.split('|')[1],
            #     'popularity': result.findAll('td')[17].text,
            #     'base_stats': result.findAll('td')[18].text
            #     'in_game_stats': result.findAll('td')[19].text
            # }

        return players



    def insert_players_into_database(self, players: []):
        if not players:
            return

        insert_rows = []

        for player in players:  # type: FutBinPlayer
            if not type(player) == FutBinPlayer:
                self.logger.error('Player not of right type: {0}'.format(type(player)))
                continue

            # self.remove_duplicate_player(player.get_url())

            insert_rows.append((
                self.site_id,
                player.get_url(),
                player.get_name(),
                player.get_country(),
                player.get_league(),
                player.get_club(),
                player.get_position(),
                player.get_cost_playstation(),
                player.get_cost_xbox(),
                player.get_cost_pc(),
                player.get_overall_rating(),
                player.get_pace(),
                player.get_shooting(),
                player.get_passing(),
                player.get_dribbling(),
                player.get_defense(),
                player.get_physical(),
                player.get_skill_moves(),
                player.get_weak_foot(),
                player.get_attacking_work_rate(),
                player.get_defensive_work_rate(),
                player.get_height_inches()
            ))

        if not insert_rows:
            self.logger.error('No players to insert into database')
            return

        conn = self.database.get_conn()
        try:
            cur = conn.cursor()

            cur.executemany("""
                INSERT INTO `Player` (
                    `SiteId`
                    ,`Url`
                    ,`Name`
                    ,`Nationality`
                    ,`League`
                    ,`Club`
                    ,`Position`
                    ,`Playstation_Cost`
                    ,`Xbox_Cost`
                    ,`Pc_Cost`
                    ,`Overall`
                    ,`Pace`
                    ,`Shooting`
                    ,`Passing`
                    ,`Dribbling`
                    ,`Defense`
                    ,`Physical`
                    ,`SkillMoves`
                    ,`WeakFootAbility`
                    ,`OffensiveWorkRate`
                    ,`DeffensiveWorkRate`
                    ,`HeightInches`
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, insert_rows)

            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            self._log_error('Failed to insert players', e)

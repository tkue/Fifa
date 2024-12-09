import sqlite3
import sys
import urllib

import requests

from WebScraping.GetData.SiteType import SiteType
from WebScraping.GetData.Config import SessionConfig

sys.path.append('../../../')

import DatabaseUtils
from NetworkUtil import NetworkUtil
from Validator import Validator
from StringUtil import StringUtil

from logging import Logger

# from ConfigUtil import Config
# import ConfigUtil



from abc import ABCMeta, abstractmethod

from bs4 import BeautifulSoup


class ISession(object):
    __metaclass__ = ABCMeta

    logger = ...  # type: Logger

    def __init__(self, config_path: str, site_type: SiteType):
        self.config = SessionConfig(config_path=config_path)
        self.logger = self.config.get_logger()
        self.site_type = site_type

        self.check_if_can_continue()

        self.database = DatabaseUtils.Sqlite3Database(
            database_path=self.config.get_database_name(),
            logger=self.logger,
            schema_script_path=self.config.get_database_schema_script()
        )

        self.insert_site_into_database()  # Need to run before getting site id
        self.site_id = self.__get_site_id()
        self.remove_old_players_in_database()

    @staticmethod
    def get_current_ip():
        return NetworkUtil.get_public_ip()

    def _log_error(self, msg: str, error=None):
        import traceback
        if msg:
            self.logger.error(msg)

        if error:
            try:
                self.logger.error(error)
            except:
                pass

        self.logger.error(traceback.format_exc())


    def is_ip_masked(self):
        original_ip = self.config.get_original_ip().strip()
        current_ip = ISession.get_current_ip()

        if not Validator.is_valid_ip_address(original_ip) or not Validator.is_valid_ip_address(current_ip):
            self.logger.critical(
                'Unable to determine if IP is masked or not because one or both IPs compared are invalid')
            self.logger.critical('Original IP: {0}\nCurrent IP: {1}'.format(original_ip, current_ip))
            raise Exception

        if original_ip != current_ip:
            return True
        else:
            self.logger.info(
                'IP address not masked:\n\tOriginal IP: {0}\n\tCurrent IP: {1}'.format(original_ip, current_ip))
            return False

    def is_can_continue_with_connection(self):
        """
        Can we continue with everything if we need to mask our IP and the IP is successfully masked?
        :return:
        :rtype:
        """

        if not self.config.get_is_need_mask_ip():
            return True

        if self.config.get_is_need_mask_ip() and self.is_ip_masked():
            return True

        return False

    def check_if_can_continue(self):
        if not self.is_can_continue_with_connection():
            self.logger.critical('IP address is not masked\nOriginal IP: {0}\nCurrent IP: {1}\nExiting...'.format(self.config.get_original_ip(), ISession.get_current_ip()))
            exit(0)

    def get_start_url(self):
        return self.config.get_start_url(self.site_type)

    def get_site_name(self):
        return self.config.get_site_name(self.site_type)

    def get_site_base_url(self):
        return self.config.get_site_base_url(self.site_type)

    def insert_site_into_database(self):
        self.logger.info('Checking if Site in database')

        conn = self.database.get_conn()
        try:
            cur = conn.cursor()

            cur.execute('SELECT Name FROM Site WHERE Name = ?', (self.get_site_name(), ))

            if not cur.fetchall() and not len(cur.fetchall()) > 0:
                self.logger.info('Site not in database. Adding...')
                cur.execute('INSERT INTO `Site` (Name, Url) VALUES(?, ?)', (self.get_site_name(), self.get_site_base_url()))
                conn.commit()
            else:
                self.logger.info('Site in database')

        except sqlite3.Error as e:
            conn.rollback()
            self._log_error('Unable to insert site record', e)
            # self.logger.error('Unable to insert site record')
            # self.logger.error(e)
            # self.logger.error(traceback.format_exc())

    def __get_site_id(self):
        try:
            conn = self.database.get_conn()
            cur = conn.cursor()

            cur.execute('SELECT SiteId FROM Site WHERE Name = ?', (self.get_site_name(), ))

            row = cur.fetchall()

            if row and len(row) > 0:
                return row[0][0]

        except sqlite3.Error as e:
            self._log_error('Unable to get SiteId', e)
            # self.logger.error('Unable to get SiteId')
            # self.logger.error(e)
            # self.logger.error(traceback.format_exc())

    def remove_old_players_in_database(self):
        conn = self.database.get_conn()

        try:
            cur = conn.cursor()

            cur.execute('DELETE FROM Player WHERE SiteId = ?', (self.site_id, ))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            self._log_error('Failed to delete players for site from Player table', e)

    @abstractmethod
    def start_session(self):
        raise NotImplementedError

    @abstractmethod
    def end_session(self):
        raise NotImplementedError

class Player(object):
    @staticmethod
    def parse_height_to_get_inches(val: str):
        """
        Parses height and returns number of inches
        :param val: Expected input: ' 6\'1"'
        :type val:
        :return:
        :rtype:
        """
        if not val:
            return

        try:
            val = val.strip()

            values = val.split('\'')
            feet = StringUtil.remove_everything_but_numbers(values[0].strip())
            inches = StringUtil.remove_everything_but_numbers(values[1].strip())

            return (12 * feet) + inches
        except:
            return None


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

    def get_cost_playstation(self):
        try:
            return self.soup.findAll('td')[4].text
        except:
            return None

    def get_cost_xbox(self):
        try:
            return self.soup.findAll('td')[5].text
        except:
            return None

    def get_cost_pc(self):
        try:
            return self.soup.findAll('td')[6].text
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



class FutBinSession(ISession):
    def __init__(self, config_path: str):
        super(FutBinSession, self).__init__(config_path, SiteType.FUTBIN)

    def start_session(self):
        self.check_if_can_continue()
        url = super().get_start_url()
        self.logger.info('Starting with URL: {0}'.format(url))

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

        results = soup.find('table', class_='table table-striped table-hover').findAll('tr')

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


class FutWizPlayer(Player):
    def __init__(self, columns: BeautifulSoup, url: str):
        self.columns = columns
        self.url = url

    def get_relative_url(self):
        try:
            return self.columns[0].find('a').attrs['href']
        except:
            return None

    def get_abs_url(self):
        try:
            return urllib.parse.urljoin(self.url, self.columns[0].find('a').attrs['href'])
        except:
            return None

    def get_name(self):
        try:
            return self.columns[1].text.split('\n')[1].strip()
        except:
            return None

    def get_club(self):
        try:
            return self.columns[1].text.split('\n')[2].split('|')[0].strip()
        except:
            return None

    def get_league(self):
        try:
            return self.columns[1].text.split('\n')[2].split('|')[1].strip()
        except:
            return None

    def get_position(self):
        try:
            return self.columns[2].text.strip()
        except:
            return None

    def get_cost(self):
        try:
            return StringUtil.remove_everything_but_numbers(self.columns[3].text)
        except:
            return None

    def get_overall(self):
        try:
            return self.columns[4].text
        except:
            return None

    def get_pace(self):
        try:
            return self.columns[5].text
        except:
            return None

    def get_shooting(self):
        try:
            return self.columns[6].text
        except:
            return None

    def get_passing(self):
        try:
            return self.columns[7].text
        except:
            return None

    def get_dribbling(self):
        try:
            return self.columns[8].text
        except:
            return None

    def get_defense(self):
        try:
            return self.columns[9].text
        except:
            return None

    def get_physical(self):
        try:
            return self.columns[10].text
        except:
            return None

    def get_skill_moves(self):
        try:
            return self.columns[11].text
        except:
            return None

    def get_week_foot(self):
        try:
            return self.columns[12].text
        except:
            return None

    def get_work_rate_offense(self):
        try:
            return self.columns[13].text.strip().split('/')[0]
        except:
            return None

    def get_work_rate_defense(self):
        try:
            return self.columns[13].text.strip().split('/')[1]
        except:
            return None

    def get_foot(self):
        try:
            return self.columns[14].text.strip()
        except:
            return None

    def get_total_stats(self):
        try:
            return StringUtil.remove_everything_but_numbers(self.columns[15].text.strip())
        except:
            return None




class FutWizSession(ISession):
    def __init__(self, config_path: str):
        super(FutWizSession, self).__init__(config_path, SiteType.FUTWIZ)

    def start_session(self):
        self.check_if_can_continue()
        url = self.config.get_start_url()
        self.logger.info('Starting with URL: {0}'.format(url))

        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        results_table = soup.find('table', class_='table table-tdc mb-20')

        # TODO: Iterate over results
        # results_table.findAll('tr')[1].findAll('td')

        players = []

        for i, row in enumerate(results_table.findAll('tr')):
            if i > 0:
                break

            columns = row.findAll('td')

            # player = {
            #     'relative_url': columns[0].find('a').attrs['href'],
            #     'abs_url': urllib.parse.urljoin(url, columns[0].find('a').attrs['href']),
            #     'name': columns[1].text.split('\n')[1].strip(),
            #     'club': columns[1].text.split('\n')[2].split('|')[0].strip(),
            #     'league': columns[1].text.split('\n')[2].split('|')[1].strip(),
            #     'position': columns[2].text.strip(),
            #     'cost': StringUtil.remove_everything_but_numbers(columns[3].text),
            #     'overall': columns[4].text,
            #     'pace': columns[5].text,
            #     'shooting': columns[6].text,
            #     'passing': columns[7].text,
            #     'dribbling': columns[8].text,
            #     'defense': columns[9].text,
            #     'physical': columns[10].text,
            #     'skill_moves': columns[11].text,
            #     'week_foot': columns[12].text,
            #     'work_rate_offense': columns[13].text.strip().split('/')[0],
            #     'work_rate_defense': columns[13].text.strip().split('/')[1],
            #     'foot': columns[14].text.strip(),
            #     'total_stats': StringUtil.remove_everything_but_numbers(columns[15].text.strip())
            # }

            player = FutWizPlayer(columns, url)

            players.append(player)

        names = []
        for player in players:
            # print(player['name'])
            names.append(player['name'])

        print(names)

    def end_session(self):
        self.logger.info('Session ended')




if __name__ == '__main__':
    # session = FutWizSession('config.json')
    # session.start_session()
    #
    session = FutBinSession('config.json')
    session.start_session()

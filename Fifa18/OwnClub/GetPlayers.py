
from Fifa18.Config import FifaConfig
from Fifa18.Database import FifaDatabase
from Fifa18.Config import WebDriverType

from StringUtil import StringUtil

from abc import ABCMeta, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup
from bs4.element import Tag

class ISession(object):
    __metaclass__ = ABCMeta

    config = ...  # type: FifaConfig

    def __init__(self, config: FifaConfig):
        self.config = config
        self.database = FifaDatabase(self.config)
        self.logger = self.config.get_logger()

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

    def _get_webdriver(self, web_driver_type: WebDriverType):
        if web_driver_type.value == WebDriverType.CHROME.value:
            opts = self.config.get_driver_options(self.web_driver_type)
            return webdriver.Chrome(executable_path=self.config.get_driver_path(self.web_driver_type),
                                    chrome_options=opts)
        else:
            raise NotImplementedError

    @abstractmethod
    def start_session(self):
        raise NotImplementedError

    @abstractmethod
    def end_session(self):
        raise NotImplementedError


class WebScrapingSession(ISession):
    def __init__(self, config: FifaConfig, web_driver_type: WebDriverType):
        super(WebScrapingSession, self).__init__(config)
        self.web_driver_type = web_driver_type
        self.start_url = self.config.get_webapp_url()
        self.driver = super()._get_webdriver(self.web_driver_type)

        self.site_id = self.get_site_id()

        self.players = []



    def start_session(self):
        self.driver.get(self.start_url)
        input('Press enter when on the list of players page')
        self.scrape_players_from_page()

        is_has_next_button = self.is_has_next_button()
        while is_has_next_button:
            if not self.go_to_next_page():
                break
            self.scrape_players_from_page()
            is_has_next_button = self.is_has_next_button()


        for player in self.players:
            print(player)


        self.insert_players_into_database(self.players)

        print(self.driver.page_source)

    def end_session(self):
        pass

    def get_next_button(self):
        try:
            return self.driver.find_element_by_xpath('//*[@id="MyClubSearch"]/section/article/div[1]/div[1]/a[2]')
        except:
            return None

    def is_has_next_button(self):
        try:
            elem = self.get_next_button()
            if elem:
                return True
        except:
            return False

    def go_to_next_page(self):
        try:
            button = self.get_next_button()
            if button:
                self.get_next_button().click()
                return True
        except NoSuchElementException as no_elem:
            self.logger.warn('Cannnot find next button: \n{}'.format(no_elem))
            return False
        except Exception as e:
            self.logger.warn('Cannot go to next page: {}'.format(e))
            return False


    def scrape_players_from_page(self):
        self.logger.info('Scraping page')

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        players = soup.find_all(class_='listFUTItem')
        all_players = []

        for player in players:
            all_players.append({
                'chemistry': player.find(class_='playStyle').text,
                'name': player.find(class_='name').text,
                'pace': StringUtil.remove_everything_but_numbers(
                    player.find(class_='secondary player-stats-data-component').find_all('li')[0].text),
                'shooting': StringUtil.remove_everything_but_numbers(
                    player.find(class_='secondary player-stats-data-component').find_all('li')[1].text),
                'passing': StringUtil.remove_everything_but_numbers(
                    player.find(class_='secondary player-stats-data-component').find_all('li')[2].text),
                'dribbling': StringUtil.remove_everything_but_numbers(
                    player.find(class_='secondary player-stats-data-component').find_all('li')[3].text),
                'defense': StringUtil.remove_everything_but_numbers(
                    player.find(class_='secondary player-stats-data-component').find_all('li')[4].text),
                'physical': StringUtil.remove_everything_but_numbers(
                    player.find(class_='secondary player-stats-data-component').find_all('li')[5].text)
            })

        for player in all_players:
            self.players.append(player)


    def get_site_id(self):
        conn = self.database.get_conn()
        try:
            cur = conn.cursor()
            row = cur.execute('SELECT SiteId FROM Site WHERE Name = ?', ('WebApp',)).fetchone()[0] #TODO: Don't hardcode

            # row = cur.fetchone()
            if not row:
                self.logger.error('Unable to get SiteId')
                return


            return row
        except Exception as e:
            self.logger.error('Unable to get SiteId: \n{}'.format(e))


    def insert_players_into_database(self, players: []):
        if not players:
            self.logger.error('No players passed to insert into database')
            return

        conn = self.database.get_conn()
        try:
            cur = conn.cursor()

            for player in players:
                try:
                    cur.execute("""INSERT INTO Player (
                        SiteId
                        ,Name
                        ,ChemistryStyle
                        ,Pace
                        ,Shooting
                        ,Passing
                        ,Dribbling
                        ,Defense
                        ,Physical
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                        self.site_id,
                        player['name'],
                        player['chemistry'],
                        player['pace'],
                        player['shooting'],
                        player['passing'],
                        player['dribbling'],
                        player['defense'],
                        player['physical'],
                    ))
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    self.logger.error('Failed to insert player row: {}\n{}'.format(player, e))
        except Exception as ex:
            self.logger.error('Failed to insert any players: {}'.format(ex))
        finally:
            conn.close()


if __name__ == '__main__':
    config = FifaConfig('../config.json')
    print(config.get_database_name())

    # print(config.get_driver_path(WebDriverType.CHROME))
    session = WebScrapingSession(config, WebDriverType.CHROME)
    session.start_session()

    # players = [
    #     {'shooting': 89, 'dribbling': 96, 'physical': 80, 'defense': 74, 'passing': 91, 'name': 'Keïta', 'pace': 81,
    #      'chemistry': 'BAS'}
    #     , {'shooting': 91, 'dribbling': 90, 'physical': 80, 'defense': 50, 'passing': 88, 'name': 'Gregoritsch',
    #        'pace': 80, 'chemistry': 'BAS'}
    #     , {'shooting': 75, 'dribbling': 89, 'physical': 65, 'defense': 72, 'passing': 86, 'name': 'Modrić', 'pace': 73,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 68, 'dribbling': 86, 'physical': 49, 'defense': 34, 'passing': 76, 'name': 'Kagawa', 'pace': 70,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 84, 'dribbling': 95, 'physical': 90, 'defense': 94, 'passing': 98, 'name': 'Kimmich', 'pace': 85,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 92, 'dribbling': 86, 'physical': 88, 'defense': 51, 'passing': 78, 'name': 'Mariano', 'pace': 89,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 70, 'dribbling': 75, 'physical': 84, 'defense': 85, 'passing': 76, 'name': 'Bender', 'pace': 80,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 86, 'dribbling': 86, 'physical': 79, 'defense': 71, 'passing': 85, 'name': 'Ramsey', 'pace': 72,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 78, 'dribbling': 92, 'physical': 85, 'defense': 34, 'passing': 78, 'name': 'Bolasie', 'pace': 93,
    #        'chemistry': 'HUN'}
    #     , {'shooting': 75, 'dribbling': 84, 'physical': 70, 'defense': 30, 'passing': 74, 'name': 'Musonda', 'pace': 89,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 87, 'dribbling': 85, 'physical': 84, 'defense': 35, 'passing': 77, 'name': 'Tosun', 'pace': 79,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 51, 'dribbling': 82, 'physical': 70, 'defense': 84, 'passing': 79, 'name': 'Rafinha', 'pace': 76,
    #        'chemistry': 'BAS'}
    #     ,
    #     {'shooting': 74, 'dribbling': 78, 'physical': 82, 'defense': 78, 'passing': 82, 'name': 'Strootman', 'pace': 67,
    #      'chemistry': 'BAS'}
    #     , {'shooting': 42, 'dribbling': 66, 'physical': 84, 'defense': 84, 'passing': 59, 'name': 'Bailly', 'pace': 78,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 86, 'dribbling': 91, 'physical': 79, 'defense': 58, 'passing': 71, 'name': 'Perin', 'pace': 81,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 84, 'dribbling': 80, 'physical': 83, 'defense': 34, 'passing': 76, 'name': 'Diego López',
    #        'pace': 77, 'chemistry': 'BAS'}
    #     ,
    #     {'shooting': 68, 'dribbling': 74, 'physical': 80, 'defense': 81, 'passing': 76, 'name': 'Piszczek', 'pace': 79,
    #      'chemistry': 'BAS'}
    #     ,
    #     {'shooting': 83, 'dribbling': 86, 'physical': 88, 'defense': 43, 'passing': 72, 'name': 'Jarstein', 'pace': 80,
    #      'chemistry': 'BAS'}
    #     , {'shooting': 63, 'dribbling': 77, 'physical': 78, 'defense': 81, 'passing': 73, 'name': 'Rose', 'pace': 81,
    #        'chemistry': 'BAS'}
    #     ,
    #     {'shooting': 80, 'dribbling': 78, 'physical': 59, 'defense': 31, 'passing': 66, 'name': 'Hernández', 'pace': 79,
    #      'chemistry': 'BAS'}
    #     , {'shooting': 73, 'dribbling': 69, 'physical': 83, 'defense': 83, 'passing': 73, 'name': 'Iborra', 'pace': 50,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 48, 'dribbling': 71, 'physical': 81, 'defense': 81, 'passing': 68, 'name': 'Medel', 'pace': 74,
    #        'chemistry': 'BAS'}
    #     ,
    #     {'shooting': 80, 'dribbling': 75, 'physical': 79, 'defense': 67, 'passing': 74, 'name': 'Klaassen', 'pace': 73,
    #      'chemistry': 'BAS'}
    #     , {'shooting': 69, 'dribbling': 84, 'physical': 69, 'defense': 61, 'passing': 82, 'name': 'Kovačić', 'pace': 81,
    #        'chemistry': 'MAE'}
    #     , {'shooting': 77, 'dribbling': 84, 'physical': 75, 'defense': 43, 'passing': 79, 'name': 'Vázquez', 'pace': 64,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 49, 'dribbling': 68, 'physical': 82, 'defense': 82, 'passing': 64, 'name': 'Keane', 'pace': 72,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 49, 'dribbling': 76, 'physical': 68, 'defense': 76, 'passing': 76, 'name': 'Weigl', 'pace': 70,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 76, 'dribbling': 84, 'physical': 64, 'defense': 62, 'passing': 79, 'name': 'Rafinha', 'pace': 74,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 80, 'dribbling': 85, 'physical': 73, 'defense': 49, 'passing': 73, 'name': 'Piatti', 'pace': 76,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 73, 'dribbling': 81, 'physical': 68, 'defense': 47, 'passing': 77, 'name': 'Shatov', 'pace': 88,
    #        'chemistry': 'BAS'}
    #     ,
    #     {'shooting': 71, 'dribbling': 79, 'physical': 72, 'defense': 61, 'passing': 80, 'name': 'Aránguiz', 'pace': 75,
    #      'chemistry': 'BAS'}
    #     , {'shooting': 67, 'dribbling': 83, 'physical': 64, 'defense': 37, 'passing': 80, 'name': 'Tadić', 'pace': 70,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 35, 'dribbling': 71, 'physical': 78, 'defense': 81, 'passing': 70, 'name': 'Stones', 'pace': 71,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 69, 'dribbling': 87, 'physical': 78, 'defense': 47, 'passing': 78, 'name': 'Ochoa', 'pace': 76,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 42, 'dribbling': 49, 'physical': 83, 'defense': 78, 'passing': 49, 'name': 'Papadopoulos',
    #        'pace': 62, 'chemistry': 'BAS'}
    #     ,
    #     {'shooting': 75, 'dribbling': 81, 'physical': 59, 'defense': 35, 'passing': 74, 'name': 'Herrmann', 'pace': 87,
    #      'chemistry': 'BAS'}
    #     , {'shooting': 76, 'dribbling': 81, 'physical': 58, 'defense': 30, 'passing': 76, 'name': 'Konoplyanka',
    #        'pace': 86, 'chemistry': 'BAS'}
    #     , {'shooting': 60, 'dribbling': 83, 'physical': 66, 'defense': 76, 'passing': 74, 'name': 'Bernat', 'pace': 78,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 79, 'dribbling': 82, 'physical': 58, 'defense': 37, 'passing': 71, 'name': 'Višća', 'pace': 89,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 50, 'dribbling': 56, 'physical': 83, 'defense': 79, 'passing': 58, 'name': 'Zouma', 'pace': 67,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 75, 'dribbling': 81, 'physical': 61, 'defense': 34, 'passing': 72, 'name': 'Lozano', 'pace': 93,
    #        'chemistry': 'BAS'}
    #     ,
    #     {'shooting': 68, 'dribbling': 78, 'physical': 68, 'defense': 69, 'passing': 82, 'name': 'Montolivo', 'pace': 56,
    #      'chemistry': 'BAS'}
    #     , {'shooting': 54, 'dribbling': 67, 'physical': 86, 'defense': 76, 'passing': 64, 'name': "N'Diaye", 'pace': 72,
    #        'chemistry': 'BAS'}
    #     , {'shooting': 62, 'dribbling': 72, 'physical': 68, 'defense': 79, 'passing': 79, 'name': 'Victor Sánchez',
    #        'pace': 64, 'chemistry': 'BAS'}
    #     , {'shooting': 33, 'dribbling': 56, 'physical': 75, 'defense': 78, 'passing': 52, 'name': 'Lenglet', 'pace': 73,
    #        'chemistry': 'BAS'}]
    #
    # session.insert_players_into_database(players)

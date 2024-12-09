import sqlite3
import sys
import urllib
from abc import ABCMeta, abstractmethod

from WebScraping.GetData.SiteType import SiteType
from WebScraping.GetData.Config import SessionConfig


import DatabaseUtils
from NetworkUtil import NetworkUtil
from Validator import Validator

from logging import Logger


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
        self.old_player_ids = self.get_list_of_current_players()

        self.start_session()
        self.end_session()

        self.remove_old_players()

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

    def get_list_of_current_players(self):
        """
        Get list of current player Ids for site
        In order to delete players at the end of a SUCCESSFUL insert of new players
        :return:
        :rtype: list
        """
        current_player_ids = []

        conn = self.database.get_conn()
        cur = conn.cursor()

        rows = cur.execute('SELECT PlayerId FROM Player WHERE SiteId = ?', (self.site_id,))

        if rows:
            for row in rows:
                current_player_ids.append(row[0])

        return current_player_ids


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

    def remove_old_players(self):
        self.logger.info('Removing old players from database')

        if not self.old_player_ids:
            self.logger.info('No older players to delete')
            return

        conn = self.database.get_conn()

        try:
            cur = conn.cursor()

            for player_id in self.old_player_ids:
                cur.execute('DELETE FROM Player WHERE PlayerId = ?', (str(player_id),))

            # cur.execute('DELETE FROM Player WHERE SiteId = ?', (self.site_id, ))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            # self._log_error('Failed to delete players for site from Player table', e)
            self._log_error('Failed to remove player. Id = {}'.format(str(player_id)))

    def remove_all_players_for_site(self):
        self.logger.info('Removing old players from database')
        conn = self.database.get_conn()

        try:
            cur = conn.cursor()

            cur.execute('DELETE FROM Player WHERE SiteId = ?', (self.site_id, ))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            self._log_error('Failed to delete players for site from Player table', e)

    def remove_duplicate_player(self,  url: str):
        if not self.site_id or not url:
            self.logger.error('Unable to remove duplicate player because values were missing')
            return


        try:
            conn = self.database.get_conn()
            cur = conn.cursor()

            rows = cur.execute("""SELECT PlayerId
                                FROM Player
                                WHERE
                                    SiteId = ? AND Url = ?""", (self.site_id, url))


            sql = None
            if rows.fetchall() > 0:
                ids = []
                for row in rows:
                    ids.append(row[0])

                ids_to_delete = self.database.generate_in_string_from_list(ids)
                sql = 'DELETE FROM Player WHERE PlayyerId IN {}'.format(ids_to_delete)

                try:
                    conn.execute(sql)
                    conn.commit()

                except sqlite3.Error as e:
                    conn.rollback()
                    self.logger.error('Failed to delete duplicate players')
                    self.logger.error('UDL: {}'.format(url))
                    self.logger.error('SQL:{}'.format(sql))
                except Exception as ex:
                    conn.rollback()
                    self.logger.error('Unable to delete duplicate rows. Unexpected error: {}'.format(ex))
        except Exception as e:
            print(e)
            self.logger.error(e)
            self.logger.error('URL: {}'.format(url))
            self.logger.error('SQL: {}'.format(sql))


    @abstractmethod
    def start_session(self):
        raise NotImplementedError

    @abstractmethod
    def end_session(self):
        raise NotImplementedError

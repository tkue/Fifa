from ConfigUtil import Config
from StringUtil import StringUtil

from WebScraping.GetData.SiteType import SiteType


class SessionConfig(Config):
    def __init__(self, config_path: str):
        super(SessionConfig, self).__init__(config_path)

    def get_database_name(self):
        # return self.config['database']['name']
        return self.get_path(self.config['database']['name'])

    def get_database_schema_script(self):
        return self.get_path(self.config['database']['schema_script'])


    def get_start_url(self, site_type: SiteType):

        for site in self.config['sites']:
            if site['name'].strip().lower() == site_type.value:
                return site['start_url']

        # return self.config['session']['start_url']

    def get_site_name(self, site_type: SiteType):

        for site in self.config['sites']:
            if site['name'].strip().lower() == site_type.value:
                return site['name']

    def get_site_base_url(self, site_type: SiteType):
        for site in self.config['sites']:
            if site['name'].strip().lower() == site_type.value:
                return site['base_url']

    def get_original_ip(self):
        """
        Original host IP address
        *** The IP address you want to mask ***
        :return:
        :rtype:
        """
        return self.config['connection']['original_public_ip']

    def get_is_need_mask_ip(self):
        is_need_mask_ip = self.config['connection']['is_need_mask_ip'].strip()
        return StringUtil.get_boolean_from_string(is_need_mask_ip)

    def get_logging_level(self):
        return self.config['logging']['level']

    def get_logger(self):
        return super().get_logger(self.get_logging_level())

    def get_start_url_by_site_type(self, site_type: SiteType):

        for site in self.config['sites']:
            if site_type.value == SiteType.FUTBIN.value:
                if site['name'] == SiteType.FUTBIN.value:
                    return site['start_url']


        # print(SiteType.value)
        #
        # print(self.config['sites'])


        # if site_type.value == SiteType.FUTBIN.value:
        #     for site in self.config.['sites']:
        #         if site['name'] == 'futbin':
        #             return site['start_url']
        #
        # if site_type.value == SiteType.FUTWIZ.value:
        #     for site in self.config['sites']:
        #         if site['name'] == 'futwiz':
        #             return site['start_url']
        #
        # raise NotImplementedError

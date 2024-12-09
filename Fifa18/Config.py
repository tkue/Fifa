import os
from enum import Enum

import ConfigUtil

import Fifa18

class WebDriverType(Enum):
    CHROME = 'chrome'


class NullValueError(Exception):
    pass


class InvalidConfigError(Exception):
    pass


class FifaConfig(ConfigUtil.Config):
    def __init__(self, config_path: str):
        super(FifaConfig, self).__init__(config_path)

    def get_this_config_path(self):
        return os.path.dirname(os.path.realpath(__file__))

    def get_path(self, path: str):
        return os.path.join(self.get_this_config_path(), path)

    def get_logger(self):
        level = self.config['logging']['level']
        return super().get_logger(level)

    def get_database_name(self):
        # return os.path.join(self.get_this_config_path(), self.config['database']['name'])
        # return os.path.join(os.path.abspath(Fifa18.__file__), self.config['database']['name'])
        return self.get_path(self.config['database']['name'])

    def get_database_schema_script(self):
        # return self.config['database']['schema_script']
        return self.get_path(self.config['database']['schema_script'])

    def get_database_setup_scripts(self):
        scripts = []
        for script in self.config['database']['setup_scripts']:
            scripts.append(self.get_path(script))

        return scripts

    def get_driver_arguments(self, driver_type: WebDriverType):
        if driver_type.value == WebDriverType.CHROME.value:

            args = []
            for arg in self.config['selenium']['chrome_driver_arguments']:
                args.append(arg)
        else:
            raise NotImplementedError

        return args

    def get_driver_options(self, driver_type: WebDriverType):
        if driver_type.value == WebDriverType.CHROME.value:
            from selenium.webdriver.chrome.options import Options as ChromeOptions

            opts = ChromeOptions()

            for arg in self.get_driver_arguments(driver_type):
                opts.add_argument(arg.strip())

            return opts

        else:
            raise NotImplementedError

    def get_driver_path(self, driver_type: WebDriverType):
        if driver_type.value == WebDriverType.CHROME.value:
            path = self.config['selenium']['chrome_driver_path']
            # return os.path.abspath(path)
            return self.get_path(path)
        else:
            raise NotImplementedError

    def _get_url_by_name(self, name: str):
        if not name:
            return

        name = name.strip().lower()
        for url in self.config['urls']:
            if url['name'].strip().lower() == name:
                return url['url']

    def get_webapp_url(self):
        return self._get_url_by_name('webapp')



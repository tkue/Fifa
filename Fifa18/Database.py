import DatabaseUtils

from .Config import FifaConfig


class FifaDatabase(DatabaseUtils.Sqlite3Database):
    def __init__(self, config: FifaConfig):
        super(FifaDatabase, self).__init__(database_path=config.get_database_name(),
                                           logger=config.get_logger(),
                                           schema_script_path=config.get_database_schema_script())

        self.config = config
        self.setup_scripts = self.config.get_database_setup_scripts()

        self.logger.info('Running setup scripts')
        self.execute_sql_scripts(self.setup_scripts)


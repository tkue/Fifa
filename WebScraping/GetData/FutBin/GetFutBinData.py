
from WebScraping.GetData.SiteType import SiteType
from WebScraping.GetData.Config import  SessionConfig
from WebScraping.GetData.FutBin.FutBinSession import FutBinSession


if __name__ == '__main__':

    config = SessionConfig('../config.json')

    start_url = config.get_start_url_by_site_type(SiteType.FUTBIN)

    session = FutBinSession('../config.json')
    session.start_session()





    print('')
   # config = SessionConfig(config_path='../config.json')

   # start_url = config.get_start_url_by_site_type(SiteType.FUTBIN)
   # print(start_url)
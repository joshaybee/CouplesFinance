
import pandas as pd
import dropbox
from private import keys
import datetime as dt

'''
dgb.grab_latest_file_path
dgb.save_latest_gnu
dgb.log_downloads
dgb.delete_latest_gnu
'''

class dboxGrabber():

    def __init__(self, accesstoken):
        self.client = dropbox.client.DropboxClient(accesstoken)

    def grab_latest_file_path(self, path):
        files = self.client.metadata(path)['contents']
        for index, file in enumerate(files):
            newest = pd.to_datetime(0)
            findex = None
            date = pd.to_datetime(file['modified'])
            if date > newest:
                findex = index
                newest = date
        filepath = files[index]['path']
        self.filepath = filepath
        return filepath

    def save_latest_gnu(self, filepath, saveas='GNUCashLatest.gnca'):
        try:
            f, metadata = self.client.get_file_and_metadata(filepath)
            out = open(saveas, 'wb')
            out.write(f.read())
            out.close()
            return True
        except:
            pass

    def log_downloads(self, filepath, logfile='partners_infinance_DL_log.csv'):
        log = pd.read_csv(logfile)
        length = len(log)
        log.loc[length] = [pd.to_datetime(dt.datetime.now()), filepath]
        log.to_csv(logfile,index=False)
        print('Log Updated')

    def delete_latest_gnu(self, prev_file):
        self.client.file_delete(prev_file)
        print('Latest GNU export was deleted.')

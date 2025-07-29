import ftplib
import unittest
import os
from unittest import mock
from src.op_parser.downloader import Downloader


class TestDownloader(unittest.TestCase):
    def setUp(self):
        self.data_dir = 'test_data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.downloader = Downloader(data_dir=self.data_dir)

    def tearDown(self):
        for f in os.listdir(self.data_dir):
            os.remove(os.path.join(self.data_dir, f))
        os.rmdir(self.data_dir)

    def test_list_local_files_empty(self):
        files = self.downloader.list_local_files()
        self.assertEqual(files, [])

    @mock.patch('ftplib.FTP')
    def test_download_file_with_retries_success(self, mock_ftp_class):
        mock_ftp = mock_ftp_class.return_value
        mock_ftp.retrbinary.side_effect = lambda cmd, callback: callback(b'test data')

        local_file = os.path.join(self.data_dir, 'test.op.gz')
        result = self.downloader.download_file_with_retries(mock_ftp, 'remote.op.gz', local_file)
        self.assertTrue(result)
        self.assertTrue(os.path.isfile(local_file))

        os.remove(local_file)

    @mock.patch('ftplib.FTP')
    def test_download_file_with_retries_fail(self, mock_ftp_class):
        mock_ftp = mock_ftp_class.return_value
        mock_ftp.retrbinary.side_effect = ftplib.error_temp('FTP error')

        local_file = os.path.join(self.data_dir, 'test.op.gz')
        result = self.downloader.download_file_with_retries(mock_ftp, 'remote.op.gz', local_file, max_retries=2,
                                                            retry_delay=0)
        self.assertFalse(result)
        self.assertFalse(os.path.isfile(local_file))

import os
import gzip
import shutil
import time
import ftplib
import logging

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self, ftp_host=None, ftp_base_dir=None, data_dir='data'):
        """
        :param ftp_host: адрес FTP сервера (если None — не скачиваем)
        :param ftp_base_dir: базовая директория на FTP
        :param data_dir: локальная папка с файлами или для сохранения
        """
        self.ftp_host = ftp_host
        self.ftp_base_dir = ftp_base_dir
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def download_file_with_retries(self, ftp, remote_file, local_file, max_retries=3, retry_delay=5):
        for attempt in range(max_retries):
            try:
                os.makedirs(os.path.dirname(local_file), exist_ok=True)
                with open(local_file, 'wb') as f:
                    ftp.retrbinary(f'RETR {remote_file}', f.write)
                return True
            except (
                ftplib.error_temp, ftplib.error_reply, ftplib.error_proto, ftplib.error_perm, ConnectionResetError
            ) as e:
                if os.path.exists(local_file):
                    try:
                        os.remove(local_file)
                    except Exception:
                        pass
                logger.warning(f'Ошибка при скачивании {remote_file} (попытка {attempt + 1}/{max_retries}): {e}')
                time.sleep(retry_delay)
        if os.path.exists(local_file):
            try:
                os.remove(local_file)
            except Exception:
                pass
        logger.error(f'Не удалось скачать {remote_file} после {max_retries} попыток')
        return False

    def download_and_unpack(self, ftp, filename):
        local_gz = os.path.join(self.data_dir, filename)
        local_op = local_gz[:-3]

        if not self.download_file_with_retries(ftp, filename, local_gz):
            logger.error(f'Не удалось скачать {filename}, пропуск')
            return None

        try:
            with gzip.open(local_gz, 'rb') as f_in, open(local_op, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(local_gz)
            logger.info(f'Распаковано {filename}')
            return local_op
        except Exception as e:
            logger.error(f'Ошибка при распаковке {filename}: {e}')
            return None

    def download_all_files(self):
        """
        Скачивает все файлы .op.gz из ftp_base_dir.
        Возвращает список локальных распакованных файлов.
        Если ftp_host не задан, возвращает пустой список.
        """
        if not self.ftp_host or not self.ftp_base_dir:
            logger.info('FTP параметры не заданы, пропускаем скачивание')
            return []

        ftp = ftplib.FTP(self.ftp_host, timeout=30)
        ftp.login('anonymous', '')
        ftp.cwd(self.ftp_base_dir)

        try:
            files = ftp.nlst()
        except Exception as e:
            logger.error(f'Ошибка получения списка файлов с FTP: {e}')
            ftp.quit()
            return []

        op_gz_files = [f for f in files if f.endswith('.op.gz')]
        op_gz_files.sort()

        downloaded_files = []
        for fname in op_gz_files:
            local_op = self.download_and_unpack(ftp, fname)
            if local_op:
                downloaded_files.append(local_op)

        ftp.quit()
        return downloaded_files

    def list_local_files(self):
        """
        Возвращает список файлов .op в локальной папке data_dir.
        """
        if not os.path.isdir(self.data_dir):
            logger.warning(f'Локальная папка {self.data_dir} не найдена')
            return []
        files = [os.path.join(self.data_dir, f) for f in os.listdir(self.data_dir) if f.endswith('.op')]
        files.sort()
        return files

    def get_files(self, download=False):
        """
        Получить файлы для обработки.
        :param download: если True — скачать с FTP, иначе взять из локальной папки.
        :return: список путей к локальным файлам .op
        """
        if download:
            return self.download_all_files()
        else:
            return self.list_local_files()

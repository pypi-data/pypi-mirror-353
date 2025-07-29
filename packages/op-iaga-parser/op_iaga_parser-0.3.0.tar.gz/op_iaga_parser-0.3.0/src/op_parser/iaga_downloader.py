import os
import requests
import csv
from datetime import datetime
from .iaga_parser import IAGA2002Parser  # Импорт парсера из соседнего файла

class IAGA2002Downloader:
    def __init__(self, data_dir='data', csv_dir='.'):
        """
        :param data_dir: папка для скачивания исходных файлов
        :param csv_dir: папка для сохранения CSV
        """
        self.data_dir = data_dir
        self.csv_dir = csv_dir
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.csv_dir, exist_ok=True)
        self.parser = IAGA2002Parser()
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def download_file(self, url, filename=None, overwrite=False):
        if not filename:
            filename = os.path.basename(url)
        base, ext = os.path.splitext(filename)
        filename_with_date = f"{base}_{self.timestamp}{ext}"
        file_path = os.path.join(self.data_dir, filename_with_date)

        if os.path.exists(file_path) and not overwrite:
            print(f"Файл уже существует: {file_path}")
            return file_path

        print(f"Скачиваем {url} ...")
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(resp.text)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при скачивании: {e}")
            return None

        print(f"Файл сохранён: {file_path}")
        return file_path

    def list_local_files(self):
        files = []
        for entry in os.listdir(self.data_dir):
            path = os.path.join(self.data_dir, entry)
            if os.path.isfile(path):
                files.append(path)
        return files

    def parse_files_to_csv(self, files, output_csv=None):
        all_records = []
        fieldnames = None

        for file_path in files:
            print(f"Парсим файл: {file_path}")
            try:
                records, headers = self.parser.parse_file(file_path)
            except Exception as e:
                print(f"Ошибка при парсинге {file_path}: {e}")
                continue

            if fieldnames is None:
                fieldnames = headers
            elif fieldnames != headers:
                print(f"Внимание: заголовки в файле {file_path} отличаются от предыдущих")

            all_records.extend(records)

        if not all_records:
            print("Нет данных для сохранения")
            return False

        if output_csv is None:
            output_csv = os.path.join(self.csv_dir, f'iaga_parsed_{self.timestamp}.csv')

        try:
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_records)
            print(f"Данные сохранены в CSV: {output_csv}")
            return True
        except Exception as e:
            print(f"Ошибка при записи в CSV: {e}")
            return False

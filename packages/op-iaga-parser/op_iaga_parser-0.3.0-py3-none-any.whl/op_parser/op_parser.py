import os
import re
import csv
from .utils import convert_value

class OpFileParser:
    def __init__(self, field_converters=None, apply_conversion=True):
        """
        :param field_converters: dict {field_name: [converter_functions]}
        :param apply_conversion: bool, применять ли конвертации (выбор пользователя)
        """
        self.field_converters = field_converters or {}
        self.apply_conversion = apply_conversion

    def parse_op_file(self, file_path):
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()
        records, fieldnames = self.parse_lines(lines)
        return records, fieldnames

    def parse_lines(self, lines):
        records = []
        fieldnames = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if not fieldnames:
                fieldnames = re.split(r'\s+', line)
                continue
            parts = re.split(r'\s+', line)
            if len(parts) < len(fieldnames):
                continue
            values = parts[:len(fieldnames)]
            record = dict(zip(fieldnames, values))
            for field, converters in self.field_converters.items():
                if field in record:
                    record[field] = convert_value(record[field], converters, self.apply_conversion)
            records.append(record)
        return records, fieldnames

    def save_to_csv(self, records, fieldnames, output_file):
        """
        Сохраняет данные в CSV с сохранением заголовков.
        """
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record)

    def parse_folder_to_csv(self, folder_path, output_file):
        """
        Парсит все .op файлы в папке folder_path и сохраняет объединённые данные в output_file.
        """
        all_records = []
        fieldnames = None

        files = [f for f in os.listdir(folder_path) if f.endswith('.op')]
        for filename in files:
            file_path = os.path.join(folder_path, filename)
            records, fnames = self.parse_op_file(file_path)
            print(f"Файл {filename} содержит {len(records)} записей")
            if fieldnames is None:
                fieldnames = fnames
            elif fieldnames != fnames:
                print(f"Внимание: заголовки в файле {filename} отличаются от предыдущих")
            all_records.extend(records)

        if not all_records:
            print("Нет данных для сохранения")
            return

        self.save_to_csv(all_records, fieldnames, output_file)
        print(f"Объединённые данные сохранены в {output_file}")

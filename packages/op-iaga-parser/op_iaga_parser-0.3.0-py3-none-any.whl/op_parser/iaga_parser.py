import re

class IAGA2002Parser:
    def __init__(self):
        pass

    def parse_file(self, file_path):
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()
        return self.parse_lines(lines)

    def parse_lines(self, lines):
        data = []
        headers = []
        data_section_started = False

        for line in lines:
            line = line.strip()
            # Удаляем символы '|' в конце строки и лишние пробелы
            line = re.sub(r'\|$', '', line).strip()
            if not line:
                continue
            if not data_section_started:
                # Ищем строку заголовков, например "DATE TIME DOY ..."
                if re.match(r'^DATE\s+TIME\s+DOY', line):
                    headers = re.split(r'\s+', line)
                    data_section_started = True
                continue
            parts = re.split(r'\s+', line)
            if len(parts) < len(headers):
                # Пропускаем строки с недостаточным числом полей
                continue
            row = dict(zip(headers, parts[:len(headers)]))
            data.append(row)

        return data, headers

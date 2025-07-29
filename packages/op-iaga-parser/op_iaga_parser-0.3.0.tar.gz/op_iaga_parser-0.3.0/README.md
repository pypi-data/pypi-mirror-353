# op_parser

**op_parser** — библиотека для скачивания, парсинга и преобразования научных данных из форматов Op и IAGA-2002. 
Предназначена для работы с климатическими и геомагнитными данными, включая NOAA и другие источники.

---

### Возможности

- Надёжная загрузка файлов по FTP с поддержкой повторных попыток и автоматической распаковкой gzip  
- Работа с локальными директориями для удобства использования уже скачанных данных  
- Парсинг формата Op с возможностью применять пользовательские функции конвертации единиц измерения  
- Универсальный парсер формата IAGA-2002 — стандарт для геомагнитных данных  
- Экспорт объединённых и преобразованных данных в CSV для последующего анализа и визуализации  

---

### Установка

Установите библиотеку через pip:

pip install op-iaga-parser

---

### Пример использования

#### Скачивание и распаковка файлов с FTP

from op_parser import Downloader

downloader = Downloader(
ftp_host='ftp.ncdc.noaa.gov',
ftp_base_dir='/pub/data/gsod',
data_dir='test_data'
)
files = downloader.get_files(download=True)
print(f"Скачано и распаковано файлов: {len(files)}")
for f in files:
print(f" - {f}")

#### Работа с локальными файлами

downloader = Downloader(data_dir='data')
files = downloader.get_files(download=False)
print(f"Найдено локальных .op файлов: {len(files)}")
for f in files:
print(f" - {f}")

#### Парсинг Op файлов и сохранение в CSV с конвертацией

from op_parser import OpFileParser, safe_float, f_to_c, inch_to_mm, mph_to_mps, mile_to_km

parser = OpFileParser(
field_converters={
'TemperatureF': [safe_float, f_to_c],
'WindSpeedMph': [safe_float, mph_to_mps],
'PrecipInches': [safe_float, inch_to_mm],
'DistanceMiles': [safe_float, mile_to_km]
},
apply_conversion=True
)
parser.parse_folder_to_csv('data', 'test_output.csv')
print("Данные сохранены в test_output.csv")

#### Парсинг файлов формата IAGA-2002

from op_parser import IAGA2002Downloader

downloader = IAGA2002Downloader(data_dir='data')

Скачивание и парсинг с сохранением в единый CSV
iaga_url = 'https://www2.irf.se/maggraphs/rt_iaga_last_hour_1sec_secondary.txt'
local_file = downloader.download_file(iaga_url)
if local_file:
downloader.parse_files_to_csv([local_file])
else:
print("Не удалось скачать файл")

#### Или парсинг локальных файлов
files_to_parse = downloader.list_local_files()
if files_to_parse:
downloader.parse_files_to_csv(files_to_parse)
else:
print("Локальные файлы не найдены")

---

### Лицензия

Проект распространяется под лицензией MIT.

---

### Контакты и поддержка

Если у вас есть вопросы или предложения, создайте issue на GitHub или свяжитесь с автором по email: xhispeco2018@gmail.com

---

op_parser — надёжный инструмент для работы с научными данными, позволяющий эффективно обрабатывать большие объёмы информации.
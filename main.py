import requests
from io import BytesIO
import sys
from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

address_ll = ",".join(sys.argv[1:])

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    pass

# Преобразуем ответ в json-объект
json_response = response.json()

# Получаем первую найденную организацию.
organization = json_response["features"][0]
# Название организации.
org_name = organization["properties"]["CompanyMetaData"]["name"]
# Адрес организации.
org_address = organization["properties"]["CompanyMetaData"]["address"]

# Получаем координаты ответа.
point = organization["geometry"]["coordinates"]
org_point = "{0},{1}".format(point[0], point[1])
delta = "0.005"

x1, y1 = map(float, address_ll.split(','))
x2, y2 = point

C = 111000 # константа для перевода градусов в метры

l = abs(x1 - x2) + abs(y1 - y2) # расчет градусов
l *= C # перевод в метры

name = organization["properties"]["name"] # считываю название орг.

tm = organization["properties"]["CompanyMetaData"]["Hours"]["text"] # считыва часы работы

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    "spn": ",".join([delta, delta]),
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": "{0},pm2dgl~{1},pm2wtl".format(org_point, address_ll)
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(
    response.content)).show()


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Информация')
        ll = QLabel(self)
        ll.setText(f"Расстояние: {int(l)}м.")
        ll.move(0, 50)
        title = QLabel(self)
        title.setText(f"Название: {name}")
        title.move(0, 150)
        time = QLabel(self)
        time.setText(f"Часы работы: {tm}")
        time.move(0, 250)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())


 # Белая метка - пользователя, зеленая - аптеки
 # пример запроса -python main.py 39.191537 51.666379

import requests
import base64
import os
from PIL import Image
import numpy as np

# Тест главной страницы
print("Главная страница:")
r = requests.get('http://localhost:5000/')
print(f"Статус: {r.status_code}")
print(f"Текст: {r.text[:100]}...")

# Тест страницы /data_to
print("\n" + "="*50)
print("Страница /data_to:")
r = requests.get('http://localhost:5000/data_to')
print(f"Статус: {r.status_code}")
print(f"Текст: {r.text[:100]}...")

# Тест /apinet (JSON API)
print("\n" + "="*50)
print("Тест /apinet (JSON API):")

# Создаём тестовое изображение
test_image_path = 'test_image.png'
if not os.path.exists(test_image_path):
    img_array = np.ones((100, 100, 3), dtype=np.uint8) * 255
    img_array[:, :, 0] = 255
    img_array[:, :, 1] = 0
    img_array[:, :, 2] = 0
    img = Image.fromarray(img_array)
    img.save(test_image_path)
    print(f"Создано тестовое изображение: {test_image_path}")

# Читаем и кодируем в base64
with open(test_image_path, 'rb') as fh:
    img_data = fh.read()
b64 = base64.b64encode(img_data).decode('utf-8')

jsondata = {'imagebin': b64}
res = requests.post('http://localhost:5000/apinet', json=jsondata)

if res.ok:
    print("Ответ сервера:")
    print(res.json())
else:
    print(f"Ошибка: {res.status_code}")

# Тест /apixml
print("\n" + "="*50)
print("Тест /apixml:")
try:
    r = requests.get('http://localhost:5000/apixml')
    print(f"Статус: {r.status_code}")
    if r.status_code == 200:
        print("HTML получен (первые 300 символов):")
        print(r.text[:300])
    else:
        print("Ошибка при запросе /apixml")
except Exception as e:
    print(f"Ошибка: {e}")
import os
import numpy as np
from PIL import Image

# Библиотеки для нейронной сети
import keras
from keras.layers import Input
from keras.models import Model
from keras.applications.resnet50 import decode_predictions
from keras.applications.resnet_v2 import ResNet50V2

# Конфигурация для GPU (если нет GPU — можно закомментировать)
try:
    from tensorflow.compat.v1 import ConfigProto
    from tensorflow.compat.v1 import InteractiveSession

    config = ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = 0.7
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)
except:
    print("GPU config not available, using CPU")

# Размеры изображений для нейронной сети
height = 224
width = 224
nh = 224
nw = 224
ncol = 3

# Загрузка предобученной модели ResNet50V2
print("Loading ResNet50V2 model...")
visible2 = Input(shape=(nh, nw, ncol), name='imginp')
resnet = ResNet50V2(
    include_top=True,
    weights='imagenet',
    input_tensor=visible2,
    input_shape=None,
    pooling=None,
    classes=1000
)
print("Model loaded successfully!")


# Функция чтения изображений из каталога
def read_image_files(files_max_count, dir_name):
    """
    Читает изображения из папки
    files_max_count: максимальное количество файлов для чтения
    dir_name: путь к папке
    """
    files = [f for f in os.listdir(dir_name) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if files_max_count > len(files):
        files_count = len(files)
    else:
        files_count = files_max_count

    image_box = []
    for file_i in range(files_count):
        img = Image.open(os.path.join(dir_name, files[file_i]))
        image_box.append(img)

    return files_count, image_box


# Функция получения результатов классификации
def getresult(image_box):
    """
    Классифицирует изображения с помощью нейронной сети
    image_box: список изображений PIL
    """
    files_count = len(image_box)
    images_resized = []

    # Нормализуем изображения и преобразуем в numpy
    for i in range(files_count):
        img_resized = image_box[i].resize((height, width))
        img_array = np.array(img_resized) / 255.0
        images_resized.append(img_array)

    images_resized = np.array(images_resized)

    # Подаем на вход сети
    out_net = resnet.predict(images_resized)

    # Декодируем ответ сети (top=1 — один лучший результат)
    decode = decode_predictions(out_net, top=1)

    return decode

# Для тестирования
# if __name__ == "__main__":
#     fcount, fimage = read_image_files(1, './static')
#     if fcount > 0:
#         decode = getresult(fimage)
#         print(decode)
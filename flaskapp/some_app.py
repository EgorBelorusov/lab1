print("Hello world")

import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, Response
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import base64
from PIL import Image
from io import BytesIO
import json
import lxml.etree as ET

app = Flask(__name__)

# Секретный ключ и настройки капчи
SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdRkLMsAAAAAE9lLEFdHE9z7IpydKebJjOlQgsh'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdRkLMsAAAAALW9rXGJxdd_ehP6Dfm7ukm9TCeB'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

# Настройка папки для загрузки
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Инициализация Bootstrap
bootstrap = Bootstrap(app)


# Функция обмена чередующихся полос (вариант 17)
def swap_stripes(image_array, direction, stripe_width):
    result = image_array.copy()
    h, w = image_array.shape[:2]

    if direction == 'vertical':
        for x in range(0, w - stripe_width, stripe_width * 2):
            end_a = min(x + stripe_width, w)
            end_b = min(x + stripe_width * 2, w)
            if end_b <= w:
                temp = result[:, x:end_a].copy()
                result[:, x:end_a] = result[:, x + stripe_width:end_b]
                result[:, x + stripe_width:end_b] = temp
    else:
        for y in range(0, h - stripe_width, stripe_width * 2):
            end_a = min(y + stripe_width, h)
            end_b = min(y + stripe_width * 2, h)
            if end_b <= h:
                temp = result[y:end_a, :].copy()
                result[y:end_a, :] = result[y + stripe_width:end_b, :]
                result[y + stripe_width:end_b, :] = temp

    return result


# Функция сохранения гистограммы цветов
def save_histogram(image_array, save_path):
# Сохраняет гистограмму распределения цветов
    plt.figure(figsize=(10, 6))
    colors = ('red', 'green', 'blue')
    labels = ('Красный', 'Зелёный', 'Синий')
    for i, (color, label) in enumerate(zip(colors, labels)):
        plt.hist(image_array[:, :, i].ravel(), bins=50, color=color, alpha=0.5, label=label)
    plt.xlabel('Интенсивность')
    plt.ylabel('Количество пикселей')
    plt.title('Гистограмма распределения цветов')
    plt.legend()
    plt.savefig(save_path)
    plt.close()


# Создаем форму для загрузки файла
class NetForm(FlaskForm):
    openid = StringField('openid', validators=[DataRequired()])
    upload = FileField('Load image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    direction = SelectField('Direction', choices=[
        ('vertical', 'Vertical'),
        ('horizontal', 'Horizontal')
    ], validators=[DataRequired()])
    stripe_width = IntegerField('Stripe width (pixels)',
                                 validators=[DataRequired(), NumberRange(min=1, max=200)],
                                 default=20)
    recaptcha = RecaptchaField()
    submit = SubmitField('send')


# Маршруты
@app.route("/")
def hello():
    return "<html><head></head><body>Hello World!</body></html>"


@app.route("/data_to")
def data_to():
    some_pars = {'user': 'Ivan', 'color': 'red'}
    some_str = 'Hello my dear friends!'
    some_value = 10
    return render_template('simple.html',
                           some_str=some_str,
                           some_value=some_value,
                           some_pars=some_pars)


@app.route("/net", methods=['GET', 'POST'])
def net():
    form = NetForm()
    original_image_url = None
    result_image_url = None
    histogram_url = None
    error = None

    if form.validate_on_submit():
        try:
            # Создаём папку
            upload_folder = 'static/uploads'
            os.makedirs(upload_folder, exist_ok=True)

            # Сохраняем загруженный файл
            f = form.upload.data
            filename = secure_filename(f.filename)
            original_path = os.path.join(upload_folder, 'original_' + filename)
            f.save(original_path)

            # Открываем изображение
            img = Image.open(original_path).convert('RGB')
            img_array = np.array(img)

            # Сохраняем гистограмму (используем 'Agg' бэкенд для работы без GUI)
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            plt.figure(figsize=(10, 6))
            colors = ('red', 'green', 'blue')
            labels = ('Красный', 'Зелёный', 'Синий')
            for i, (color, label) in enumerate(zip(colors, labels)):
                plt.hist(img_array[:, :, i].ravel(), bins=50, color=color, alpha=0.5, label=label)
            plt.xlabel('Интенсивность')
            plt.ylabel('Количество пикселей')
            plt.title('Гистограмма распределения цветов')
            plt.legend()
            hist_path = os.path.join(upload_folder, 'histogram.png')
            plt.savefig(hist_path)
            plt.close()

            # Получаем параметры
            direction = form.direction.data
            stripe_width = form.stripe_width.data

            # Выполняем обмен полос
            result_array = swap_stripes(img_array, direction, stripe_width)

            # Сохраняем результат
            result_filename = 'result_' + filename
            result_path = os.path.join(upload_folder, result_filename)
            result_img = Image.fromarray(result_array)
            result_img.save(result_path)

            # Формируем URL
            original_image_url = f'/static/uploads/original_{filename}'
            result_image_url = f'/static/uploads/{result_filename}'
            histogram_url = '/static/uploads/histogram.png'

        except Exception as e:
            error = f"Ошибка: {str(e)}"
            print(f"ОШИБКА: {e}")

    return render_template('net.html',
                           form=form,
                           original_image=original_image_url,
                           result_image=result_image_url,
                           histogram=histogram_url,
                           error=error)


@app.route("/apinet", methods=['GET', 'POST'])
def apinet():
    neurodic = {}
    if request.mimetype == 'application/json':
        data = request.get_json()
        filebytes = data['imagebin'].encode('utf-8')
        cfile = base64.b64decode(filebytes)
        img = Image.open(BytesIO(cfile))
        img_array = np.array(img)

        h, w = img_array.shape[:2]
        neurodic['width'] = str(w)
        neurodic['height'] = str(h)
        neurodic['format'] = str(img.format)

        ret = json.dumps(neurodic)
        resp = Response(response=ret, status=200, mimetype="application/json")
        return resp


@app.route("/apixml", methods=['GET', 'POST'])
def apixml():
    dom = ET.parse("./static/xml/file.xml")
    xslt = ET.parse("./static/xml/file.xslt")
    transform = ET.XSLT(xslt)
    newhtml = transform(dom)
    strfile = ET.tostring(newhtml)
    return strfile


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
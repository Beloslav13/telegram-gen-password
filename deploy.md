# Инструкция по деплую бота на сервер.

Зайти на сервер<br>
`ssh user@IP`<br>
Выполняем команды сразу в консоле:<br>
`apt update`<br>
`apt install -y htop git build-essential libssl-dev libffi-dev python3-pip python3-dev python3-setuptools python3-venv`<br>

Создать пользователя:<br>

`adduser user`<br>
Переключиться на нового пользователя:<br>

`whoami`<br>
`su - user`<br>
`whoami`<br>
Клонировать репозиторий:<br>

`cd /home/user`<br>
`git clone ...`<br>
Создать вирутальное окружение:<br>

`cd /home/user/my-dir`<br>
`python3 -m venv .venv`<br>
Активировать вирутальное окружение и установить пакеты:<br>

`source /home/user/my-dir/.venv/bin/activate`<br>
`pip install -r /home/user/my-dir/pip-requirements.txt`<br>
Проверить что бот работает (из виртуального окружения):<br>

`/home/user/my-dir/.venv/bin/python /home/user/my-dir/main.py`<br>
Использовать конфиг для автоматического запуска "tgbot.service"<br>

Прописать в нём своего пользователя, пути и положить его в папку (из-под root):<br>

`sudo cp /home/user/my-dir/tgbot.service /etc/systemd/system/tgbot.service`<br>
Запустить бота:<br>

`sudo systemctl start tgbot`<br>
`sudo systemctl enable tgbot`<br>
Проверить как дела:<br>

`sudo systemctl status tgbot`<br>

Перезагрузка<br>
`systemctl daemon-reload`<br>
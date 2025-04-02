# readme

Это клиентское приложение для tunnel.email

## Установка
Установите клиенсткое приложение с официального сайта https://tunnel.email

## Сборка
```bash
pip install -r requirements.txt
python3 download_rathole.py <your-os>
```
### Запустить через python3:
```bash
python3 main.py
```
### Собрать через pyinstaller:
```bash
pyinstaller --onefile --noconsole --add-data "rathole:." main.py # linux/macos
pyinstaller --onefile --noconsole --add-data "rathole.exe;." main.py # windows
```
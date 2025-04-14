# readme

Это клиентское приложение для tunnel.email

## Установка
Установите клиенсткое приложение с официального сайта https://tunnel.email

## Сборка из исходного кода
```bash
pip install -r requirements.txt
python3 download_rathole.py <your-os>
```
### Запустить через python3:
```bash
python3 main.py
```
### Собрать через nuitka (рекомендуется)
```bash
nuitka --enable-plugin=pyside6 --onefile --windows-disable-console --include-data-files=rathole=rathole main.py # linux/macos
nuitka --enable-plugin=pyside6 --onefile --windows-disable-console --include-data-files=rathole=rathole.exe main.py # windows
```

### Собрать через pyinstaller:
```bash
pyinstaller --onefile --noconsole --add-data "rathole:." main.py # linux/macos
pyinstaller --onefile --noconsole --add-data "rathole.exe;." main.py # windows
```
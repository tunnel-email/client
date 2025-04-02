import sys
import os
import zipfile
import requests

def download_file(url, output_filename):
    print(f"Скачивание rathole 4.8: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(output_filename, 'wb') as f:
            f.write(response.content)

        return True
    except Exception as e:
        print(f"Ошибка при download_file: {e}")

        return False

def extract_zip(zip_path, extract_to='.'):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            zip_ref.extractall(extract_to)
            
            for file in file_list:
                # chmod +x
                if os.path.isfile(os.path.join(extract_to, file)) and sys.platform != "win32":
                    try:
                        os.chmod(os.path.join(extract_to, file), 0o755)
                    except:
                        pass
        return True
    except Exception as e:
        print(f"Ошибка при extract_zip: {e}")
        return False

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["windows", "linux", "macos"]:
        print("Использование: python3 download_rathole.py windows|linux|macos")
        sys.exit(1)
    
    urls = {
        "windows": "https://github.com/rapiz1/rathole/releases/download/v0.4.8/rathole-x86_64-pc-windows-msvc.zip",
        "linux": "https://github.com/rapiz1/rathole/releases/download/v0.4.8/rathole-x86_64-unknown-linux-gnu.zip",
        "macos": "https://github.com/rapiz1/rathole/releases/download/v0.4.8/rathole-x86_64-apple-darwin.zip"
    }
    
    os_type = sys.argv[1]

    url = urls[os_type]
    filename = url.split('/')[-1]
    
    if download_file(url, filename):
        if extract_zip(filename):
            # удаление архива
            try:
                os.remove(filename)

                print("rathole скачан")
            except Exception as e:
                print(f"Не удалось удалить архив {filename}: {e}")
        else:
            print("Ошибка")
    else:
        print("Ошибка")

if __name__ == "__main__":
    main()

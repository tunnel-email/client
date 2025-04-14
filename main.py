import os
os.environ['QT_PREFERRED_BINDING'] = 'PySide6' # pyside6 backend

import sys
import traceback
from Qt import QtWidgets
from app.app import EmailTunnelApp
from app.utils.logger import setup_logger


logger = setup_logger("main")

def excepthook(exc_type, exc_value, exc_tb):
    # обработчик исключений
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.critical(f"Необработанное исключение: {error_msg}")
    
    # показываем пользователю сообщение об ошибке
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)
    msg_box.setWindowTitle("Критическая ошибка")
    msg_box.setText("Произошла непредвиденная ошибка в приложении")
    msg_box.setDetailedText(error_msg)
    msg_box.exec_()

def main():
    logger.info("Запуск приложения")
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("Fusion")
        
        sys.excepthook = excepthook
        
        from app.utils.styles import apply_global_styles
        apply_global_styles(app)
        
        window = EmailTunnelApp()
        window.show()
        
        exit_code = app.exec_()
        logger.info(f"Приложение завершено с кодом: {exit_code}")
        return exit_code
    except Exception as e:
        logger.critical(f"Ошибка в main: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())

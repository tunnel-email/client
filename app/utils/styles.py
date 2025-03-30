def apply_global_styles(app):
    app.setStyleSheet("""
        QMainWindow, QDialog {
            background: #121212;
            color: #e0e0e0
        }
        
        QPushButton {
            /* Отключаем прозрачность */
            background: #0d6efd !important;
            opacity: 1;
            
            color: white !important;
            border: 1px solid #0a58ca;
            border-bottom: 3px solid #0a58ca;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            margin: 2px;
        }
        
        /* Явно указываем стили для разных состояний */
        QPushButton:hover {
            background: #0b5ed7 !important;
            border-bottom: 3px solid #084298;
        }
        
        QPushButton:pressed {
            background: #084298 !important;
            border-bottom: 1px solid #084298;
        }
        
        QPushButton:disabled {
            background: #6c757d !important;
            color: #dddddd !important;
            border: 1px solid #565e64;
            border-bottom: 3px solid #565e64;
        }
    """)

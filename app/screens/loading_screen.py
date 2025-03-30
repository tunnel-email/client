from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class LoadingScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        progress_label = QLabel("Создание туннеля и получение сертификата...")
        progress_label.setAlignment(Qt.AlignCenter)
        progress_label.setFont(QFont('Arial', 14))
        progress_label.setStyleSheet("color: #e0e0e0; margin-bottom: 20px;")
        layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.progress_bar.setFixedSize(400, 30)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                text-align: center;
                color: #e0e0e0;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        
        progress_layout = QHBoxLayout()
        progress_layout.addStretch()
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addStretch()
        layout.addLayout(progress_layout)

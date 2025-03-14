import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from ui.main_window import VocabularyApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Thiết lập font mặc định
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Thiết lập style sheet toàn cục
    with open("ui/styles/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    
    window = VocabularyApp()
    window.show()
    sys.exit(app.exec_()) 
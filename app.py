import sys
import os
import traceback

# Bắt lỗi và hiển thị
def exception_hook(exctype, value, tb):
    print(''.join(traceback.format_exception(exctype, value, tb)))
    sys.exit(1)

sys.excepthook = exception_hook

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from ui.main_window import VocabularyApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Tạo thư mục cần thiết
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/categories", exist_ok=True)
    os.makedirs("data/categories/Chung", exist_ok=True)
    os.makedirs("ui/images", exist_ok=True)
    
    # Thiết lập font mặc định
    font = QFont("Segoe UI", 9)  # Giảm kích thước font
    app.setFont(font)
    
    # Thiết lập biểu tượng ứng dụng
    logo_path = "ui/images/logo.png"
    if os.path.exists(logo_path):
        app_icon = QIcon(logo_path)
        app.setWindowIcon(app_icon)
    
    # Thiết lập style sheet toàn cục
    style_path = "ui/styles/style.qss"
    if os.path.exists(style_path):
        with open(style_path, "r", encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    
    try:
        window = VocabularyApp()
        window.show()
    except Exception as e:
        print(f"Lỗi khi tạo cửa sổ chính: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
    
    sys.exit(app.exec_()) 
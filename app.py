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
    
    # Xác định thư mục gốc của ứng dụng
    if getattr(sys, 'frozen', False):
        # Nếu đang chạy từ file .exe (đã đóng gói)
        application_path = os.path.dirname(sys.executable)
    else:
        # Nếu đang chạy từ mã nguồn
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Tạo thư mục cần thiết
    data_dir = os.path.join(application_path, "data")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, "categories"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "categories", "Chung"), exist_ok=True)
    
    # Thiết lập biến môi trường để các module khác có thể truy cập
    os.environ['FLASHLEARNVN_DATA_DIR'] = data_dir
    
    # Thiết lập font mặc định
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Thiết lập biểu tượng ứng dụng
    logo_path = os.path.join(application_path, "ui", "images", "logo.png")
    if os.path.exists(logo_path):
        app_icon = QIcon(logo_path)
        app.setWindowIcon(app_icon)
    
    # Thiết lập style sheet toàn cục
    style_path = os.path.join(application_path, "ui", "styles", "style.qss")
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
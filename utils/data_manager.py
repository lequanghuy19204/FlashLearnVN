import os
import json
from PyQt5.QtWidgets import QMessageBox

class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Đảm bảo thư mục data tồn tại"""
        data_dir = os.path.dirname(self.file_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def load_data(self):
        """Tải dữ liệu từ file JSON"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Lỗi khi tải dữ liệu: {str(e)}")
                return {}
        return {}
    
    def save_data(self, data):
        """Lưu dữ liệu vào file JSON"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu: {str(e)}")
            return False 
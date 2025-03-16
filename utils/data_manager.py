import os
import json
import shutil
from PyQt5.QtWidgets import QMessageBox

class DataManager:
    def __init__(self):
        # Sử dụng thư mục dữ liệu từ biến môi trường hoặc mặc định
        self.data_dir = os.environ.get('FLASHLEARNVN_DATA_DIR', 'data')
        self.categories_dir = os.path.join(self.data_dir, "categories")
        
        # Đảm bảo thư mục tồn tại
        os.makedirs(self.categories_dir, exist_ok=True)
        os.makedirs(os.path.join(self.categories_dir, "Chung"), exist_ok=True)
    
    def ensure_data_dirs(self):
        """Đảm bảo các thư mục dữ liệu tồn tại"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.categories_dir, exist_ok=True)
    
    def get_category_path(self, category):
        """Lấy đường dẫn đến thư mục danh mục"""
        return os.path.join(self.categories_dir, category)
    
    def get_set_path(self, category, set_name):
        """Lấy đường dẫn đến file bộ từ vựng"""
        category_path = self.get_category_path(category)
        return os.path.join(category_path, f"{set_name}.json")
    
    def load_all_data(self):
        """Tải tất cả dữ liệu từ vựng từ các thư mục danh mục"""
        vocabulary_sets = {}
        
        # Đảm bảo thư mục danh mục tồn tại
        self.ensure_data_dirs()
        
        # Duyệt qua tất cả các thư mục danh mục
        for category in self.get_categories():
            category_path = self.get_category_path(category)
            
            # Đảm bảo thư mục danh mục tồn tại
            if not os.path.exists(category_path):
                os.makedirs(category_path, exist_ok=True)
                continue
            
            # Duyệt qua tất cả các file JSON trong thư mục danh mục
            try:
                for file_name in os.listdir(category_path):
                    if file_name.endswith('.json'):
                        set_name = os.path.splitext(file_name)[0]
                        file_path = os.path.join(category_path, file_name)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                vocab_data = json.load(f)
                                
                                # Tạo khóa duy nhất cho mỗi bộ từ vựng bằng cách kết hợp tên và danh mục
                                unique_key = f"{category}::{set_name}"
                                
                                # Thêm thông tin danh mục vào dữ liệu
                                if isinstance(vocab_data, dict):
                                    vocab_data['category'] = category
                                    vocab_data['set_name'] = set_name
                                elif isinstance(vocab_data, list):
                                    vocab_data = {
                                        'items': vocab_data, 
                                        'category': category,
                                        'set_name': set_name
                                    }
                                
                                vocabulary_sets[unique_key] = vocab_data
                        except Exception as e:
                            print(f"Lỗi khi tải file {file_path}: {str(e)}")
            except Exception as e:
                print(f"Lỗi khi đọc thư mục {category_path}: {str(e)}")
        
        return vocabulary_sets
    
    def get_category_sets(self, category):
        """Lấy tất cả bộ từ vựng trong một danh mục cụ thể"""
        category_sets = {}
        all_sets = self.load_all_data()
        
        for set_key, set_data in all_sets.items():
            if set_key.startswith(f"{category}::"):
                category_sets[set_key] = set_data
        
        return category_sets
    
    def save_vocab_set(self, set_name, vocab_data, category="Chung"):
        """Lưu bộ từ vựng vào file JSON trong thư mục danh mục"""
        # Đảm bảo thư mục danh mục tồn tại
        category_path = self.get_category_path(category)
        os.makedirs(category_path, exist_ok=True)
        
        # Đường dẫn đến file JSON
        file_path = self.get_set_path(category, set_name)
        
        try:
            # Chuẩn bị dữ liệu để lưu
            save_data = vocab_data
            if 'category' in save_data:
                # Không lưu thông tin danh mục trong file (vì đã lưu trong cấu trúc thư mục)
                save_data = save_data.copy()
                save_data.pop('category')
            
            # Lưu dữ liệu vào file JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Lỗi khi lưu file {file_path}: {str(e)}")
            return False
    
    def delete_vocab_set(self, set_name, category):
        """Xóa bộ từ vựng"""
        file_path = self.get_set_path(category, set_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"Lỗi khi xóa file {file_path}: {str(e)}")
        return False
    
    def get_categories(self):
        """Lấy danh sách các danh mục"""
        categories = []
        try:
            # Đảm bảo thư mục danh mục tồn tại
            self.ensure_data_dirs()
            
            if os.path.exists(self.categories_dir):
                for item in os.listdir(self.categories_dir):
                    item_path = os.path.join(self.categories_dir, item)
                    if os.path.isdir(item_path):
                        categories.append(item)
            
            # Đảm bảo luôn có danh mục "Chung"
            if "Chung" not in categories:
                os.makedirs(os.path.join(self.categories_dir, "Chung"), exist_ok=True)
                categories.append("Chung")
            
            return sorted(categories)
        except Exception as e:
            print(f"Lỗi khi lấy danh sách danh mục: {str(e)}")
            return ["Chung"]  # Trả về danh mục mặc định nếu có lỗi
    
    def create_category(self, category_name):
        """Tạo danh mục mới"""
        category_path = self.get_category_path(category_name)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
            return True
        return False
    
    def rename_category(self, old_name, new_name):
        """Đổi tên danh mục"""
        old_path = self.get_category_path(old_name)
        new_path = self.get_category_path(new_name)
        
        if os.path.exists(old_path) and not os.path.exists(new_path):
            try:
                shutil.move(old_path, new_path)
                return True
            except Exception as e:
                print(f"Lỗi khi đổi tên danh mục: {str(e)}")
        return False
    
    def delete_category(self, category_name):
        """Xóa danh mục"""
        if category_name == "Chung":
            return False  # Không cho phép xóa danh mục "Chung"
        
        category_path = self.get_category_path(category_name)
        if os.path.exists(category_path):
            try:
                # Di chuyển tất cả các bộ từ vựng sang danh mục "Chung"
                common_path = self.get_category_path("Chung")
                os.makedirs(common_path, exist_ok=True)
                
                for file_name in os.listdir(category_path):
                    if file_name.endswith('.json'):
                        old_file_path = os.path.join(category_path, file_name)
                        new_file_path = os.path.join(common_path, file_name)
                        
                        # Nếu file đã tồn tại trong "Chung", thêm hậu tố
                        if os.path.exists(new_file_path):
                            base_name, ext = os.path.splitext(file_name)
                            new_file_path = os.path.join(common_path, f"{base_name}_from_{category_name}{ext}")
                        
                        shutil.move(old_file_path, new_file_path)
                
                # Xóa thư mục danh mục
                shutil.rmtree(category_path)
                return True
            except Exception as e:
                print(f"Lỗi khi xóa danh mục: {str(e)}")
        return False
    
    def move_vocab_set(self, set_name, old_category, new_category):
        """Di chuyển bộ từ vựng sang danh mục khác"""
        old_file_path = self.get_set_path(old_category, set_name)
        new_file_path = self.get_set_path(new_category, set_name)
        
        # Đảm bảo thư mục đích tồn tại
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        
        if os.path.exists(old_file_path):
            try:
                # Nếu file đã tồn tại trong danh mục đích, thêm hậu tố
                if os.path.exists(new_file_path):
                    base_name, ext = os.path.splitext(set_name)
                    new_file_path = os.path.join(os.path.dirname(new_file_path), 
                                               f"{base_name}_from_{old_category}{ext}")
                
                shutil.move(old_file_path, new_file_path)
                return True
            except Exception as e:
                print(f"Lỗi khi di chuyển bộ từ vựng: {str(e)}")
        return False
    
    def check_vocab_set_exists(self, set_name, category):
        """Kiểm tra xem bộ từ vựng có tồn tại trong danh mục cụ thể không"""
        file_path = self.get_set_path(category, set_name)
        return os.path.exists(file_path) 
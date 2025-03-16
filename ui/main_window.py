import os
import json
import shutil
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTextEdit, QPushButton, QLineEdit, 
                            QMessageBox, QListWidget, QListWidgetItem, QFileDialog, QStackedWidget,
                            QToolButton, QSizePolicy, QFrame, QSpacerItem,
                            QTreeWidget, QTreeWidgetItem, QSplitter, QComboBox,
                            QInputDialog, QMenu, QAction, QFormLayout)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap
import qtawesome as qta

from ui.flashcard_widget import FlashcardWidget
from utils.data_manager import DataManager

class VocabularyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.vocabulary_sets = self.data_manager.load_all_data()
        self.current_set_name = ""
        self.current_category = "Chung"
        self.categories = self.load_categories()
        self.initUI()
        
    def initUI(self):
        """Khởi tạo giao diện người dùng"""
        # Thiết lập cửa sổ chính
        self.setWindowTitle("FlashLearnVN - Ứng dụng học từ vựng")
        self.setMinimumSize(400, 400)
        
        # Tạo widget trung tâm và layout chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tạo stacked widget để chuyển đổi giữa các trang
        self.stacked_widget = QStackedWidget()
        
        # Tạo các trang
        self.main_page = QWidget()
        self.edit_page = QWidget()
        self.flashcard_page = QWidget()
        
        # Thiết lập các trang
        self.setup_edit_page()  # Gọi trước để khởi tạo category_combo
        self.setup_main_page()
        
        # Thêm các trang vào stacked widget
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.edit_page)
        self.stacked_widget.addWidget(self.flashcard_page)
        
        # Thêm stacked widget vào layout chính
        main_layout.addWidget(self.stacked_widget)
        
        # Hiển thị trang chính ban đầu
        self.stacked_widget.setCurrentIndex(0)
        
        # Cập nhật giao diện
        self.update_category_tree()
        self.update_vocab_sets_list()
        
    def setup_main_page(self):
        """Thiết lập trang chính với danh sách bộ từ vựng"""
        layout = QVBoxLayout(self.main_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Nội dung chính
        content = QSplitter(Qt.Horizontal)
        
        # Panel bên trái - Danh mục
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #f8f9fa;")
        left_panel.setMaximumWidth(200)  # Giảm chiều rộng
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(1, 1, 1, 1)  # Giảm padding
        
        # Tiêu đề danh mục
        category_header = QFrame()
        category_header.setStyleSheet("background-color: #e9ecef;")
        category_header.setMaximumHeight(25)  # Giảm chiều cao
        category_header_layout = QHBoxLayout(category_header)
        category_header_layout.setContentsMargins(3, 1, 3, 1)  # Giảm padding
        
        category_title = QLabel("Danh mục")
        category_title.setFont(QFont("Segoe UI", 8, QFont.Bold))  # Giảm kích thước font
        category_header_layout.addWidget(category_title)
        
        # Nút thêm danh mục
        add_category_btn = QToolButton()
        add_category_btn.setIcon(qta.icon('fa5s.plus', color='#3498db'))
        add_category_btn.setToolTip("Thêm danh mục mới")
        add_category_btn.setIconSize(QSize(12, 12))  # Giảm kích thước icon
        add_category_btn.clicked.connect(self.add_category)
        category_header_layout.addWidget(add_category_btn)
        
        left_panel_layout.addWidget(category_header)
        
        # Cây danh mục
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderHidden(True)
        self.category_tree.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: #f8f9fa;
            }
            QTreeWidget::item {
                height: 20px;  /* Giảm chiều cao item */
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        self.category_tree.itemClicked.connect(self.category_selected)
        self.category_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.category_tree.customContextMenuRequested.connect(self.show_category_context_menu)
        left_panel_layout.addWidget(self.category_tree)
        
        # Panel bên phải - Danh sách từ vựng
        right_panel = QFrame()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(1, 1, 1, 1)  # Giảm padding
        
        # Tiêu đề bộ từ vựng
        vocab_header = QFrame()
        vocab_header.setStyleSheet("background-color: #e9ecef;")
        vocab_header.setMaximumHeight(25)  # Giảm chiều cao
        vocab_header_layout = QHBoxLayout(vocab_header)
        vocab_header_layout.setContentsMargins(3, 1, 3, 1)  # Giảm padding
        
        self.vocab_title = QLabel("Tất cả bộ từ vựng")
        self.vocab_title.setFont(QFont("Segoe UI", 10, QFont.Bold))  # Giảm kích thước font
        vocab_header_layout.addWidget(self.vocab_title)
        
        # Nút thêm bộ từ vựng
        add_vocab_btn = QToolButton()
        add_vocab_btn.setIcon(qta.icon('fa5s.plus', color='#3498db'))
        add_vocab_btn.setToolTip("Thêm bộ từ vựng mới")
        add_vocab_btn.setIconSize(QSize(12, 12))  # Giảm kích thước icon
        add_vocab_btn.clicked.connect(self.create_new_set)
        vocab_header_layout.addWidget(add_vocab_btn)
        
        right_panel_layout.addWidget(vocab_header)
        
        # Danh sách bộ từ vựng
        self.vocab_sets_list = QListWidget()
        self.vocab_sets_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: white;
            }
            QListWidget::item {
                height: 25px;  /* Giảm chiều cao item */
                border-bottom: 1px solid #f1f2f6;
                padding: 3px;  /* Giảm padding */
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        self.vocab_sets_list.itemDoubleClicked.connect(self.start_flashcard)
        self.vocab_sets_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.vocab_sets_list.customContextMenuRequested.connect(self.show_vocab_context_menu)
        right_panel_layout.addWidget(self.vocab_sets_list)
        
        # Thêm các panel vào splitter
        content.addWidget(left_panel)
        content.addWidget(right_panel)
        content.setSizes([100, 300])  # Thiết lập kích thước ban đầu
        
        # Thêm nội dung vào layout chính
        layout.addWidget(content)
        
        # Cập nhật danh sách danh mục và bộ từ vựng
        self.update_category_tree()
        self.update_vocab_sets_list()
    
    def setup_edit_page(self):
        """Thiết lập trang thêm/chỉnh sửa từ vựng"""
        edit_layout = QVBoxLayout(self.edit_page)
        
        # Form layout cho tên bộ từ vựng và danh mục
        form_layout = QFormLayout()
        
        # Tên bộ từ vựng
        self.set_name_edit = QLineEdit()
        self.set_name_edit.setPlaceholderText("Nhập tên bộ từ vựng")
        form_layout.addRow("Tên bộ từ vựng:", self.set_name_edit)
        
        # Danh mục
        self.category_combo = QComboBox()
        self.update_category_combo()  # Cập nhật danh sách danh mục
        form_layout.addRow("Danh mục:", self.category_combo)
        
        edit_layout.addLayout(form_layout)
        
        # Hướng dẫn
        instruction_label = QLabel("Nhập từ vựng theo định dạng: mỗi từ một dòng, nghĩa ở dòng tiếp theo, sau đó là dòng trống")
        instruction_label.setWordWrap(True)
        instruction_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        edit_layout.addWidget(instruction_label)
        
        # Trình soạn thảo từ vựng
        self.vocab_edit = QTextEdit()
        self.vocab_edit.setPlaceholderText("Ví dụ:\nhello\nxin chào\n\nworld\nthế giới")
        edit_layout.addWidget(self.vocab_edit)
        
        # Các nút
        button_layout = QHBoxLayout()
        
        # Nút hủy
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setIcon(qta.icon('fa5s.times', color='#e74c3c'))
        self.cancel_button.clicked.connect(self.switch_to_main_page)
        button_layout.addWidget(self.cancel_button)
        
        # Nút lưu
        self.save_button = QPushButton("Lưu")
        self.save_button.setIcon(qta.icon('fa5s.save', color='#2ecc71'))
        self.save_button.clicked.connect(self.add_vocabulary)
        button_layout.addWidget(self.save_button)
        
        edit_layout.addLayout(button_layout)
    
    def create_tool_button(self, icon, text):
        """Tạo nút công cụ với icon và text"""
        button = QToolButton()
        button.setIcon(icon)
        button.setText(text)
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button.setIconSize(QSize(32, 32))
        button.setMinimumSize(QSize(80, 80))
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return button
    
    def update_category_tree(self):
        """Cập nhật cây danh mục"""
        self.category_tree.clear()
        
        # Thêm các danh mục vào cây
        for category in self.categories:
            category_item = QTreeWidgetItem(self.category_tree)
            category_item.setText(0, category)
            category_item.setIcon(0, qta.icon('fa5s.folder', color='#f39c12'))
            category_item.setData(0, Qt.UserRole, category)
        
        # Mở rộng tất cả các mục
        self.category_tree.expandAll()
        
        # Chọn mục "Chung" mặc định
        for i in range(self.category_tree.topLevelItemCount()):
            item = self.category_tree.topLevelItem(i)
            if item.data(0, Qt.UserRole) == "Chung":
                self.category_tree.setCurrentItem(item)
                break
    
    def update_category_combo(self):
        """Cập nhật danh sách danh mục trong combobox"""
        # Kiểm tra xem category_combo đã được khởi tạo chưa
        if not hasattr(self, 'category_combo'):
            return
        
        # Lưu lại danh mục đang chọn
        current_category = self.category_combo.currentText()
        
        # Xóa tất cả các mục hiện tại
        self.category_combo.clear()
        
        # Thêm mục mặc định
        self.category_combo.addItem("Chung")
        
        # Lấy danh sách danh mục từ data_manager
        categories = self.data_manager.get_categories()
        
        # Thêm các danh mục vào combobox
        for category in categories:
            if category != "Chung":  # Đã thêm "Chung" ở trên
                self.category_combo.addItem(category)
        
        # Chọn lại danh mục trước đó nếu có
        if current_category:
            index = self.category_combo.findText(current_category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
    
    def update_vocab_sets_list(self, category=None):
        """Cập nhật danh sách bộ từ vựng"""
        self.vocab_sets_list.clear()
        
        if category is None:
            category = self.current_category
        
        # Lọc bộ từ vựng theo danh mục
        filtered_sets = {}
        for set_name, vocab_data in self.vocabulary_sets.items():
            # Kiểm tra xem set_name có chứa thông tin danh mục không
            if "::" in set_name:
                set_category, actual_set_name = set_name.split("::", 1)
                
                if set_category == category:
                    # Chỉ hiển thị bộ từ vựng thuộc danh mục được chọn
                    filtered_sets[set_name] = vocab_data
        
        # Thêm các bộ từ vựng vào danh sách
        for set_name, vocab_data in filtered_sets.items():
            # Đếm số từ trong bộ từ vựng
            num_words = 0
            if isinstance(vocab_data, list):
                num_words = len(vocab_data)
            elif isinstance(vocab_data, dict) and 'items' in vocab_data:
                num_words = len(vocab_data['items'])
            
            # Lấy tên hiển thị (bỏ tiền tố danh mục nếu có)
            display_name = set_name
            if "::" in set_name:
                _, display_name = set_name.split("::", 1)
            
            # Tạo item với tên bộ từ vựng và số từ
            item = QListWidgetItem(f"{display_name} ({num_words} từ)")
            item.setData(Qt.UserRole, set_name)  # Lưu tên thật của bộ từ vựng
            self.vocab_sets_list.addItem(item)
    
    def category_selected(self, item):
        """Xử lý khi người dùng chọn danh mục"""
        if item:
            category = item.data(0, Qt.UserRole)
            self.current_category = category
            self.update_vocab_sets_list(category)
    
    def add_category(self):
        """Thêm danh mục mới"""
        category_name, ok = QInputDialog.getText(
            self, 'Thêm danh mục', 'Nhập tên danh mục mới:')
        
        if ok and category_name:
            if category_name in self.categories:
                QMessageBox.warning(self, 'Cảnh báo', 'Danh mục này đã tồn tại!')
                return
            
            if self.data_manager.create_category(category_name):
                self.categories = self.data_manager.get_categories()
                self.update_category_tree()
                QMessageBox.information(self, 'Thành công', f'Đã tạo danh mục "{category_name}"')
            else:
                QMessageBox.critical(self, 'Lỗi', f'Không thể tạo danh mục "{category_name}"')
    
    def show_category_context_menu(self, position):
        """Hiển thị menu ngữ cảnh cho danh mục"""
        item = self.category_tree.itemAt(position)
        if not item:
            return
        
        category = item.data(0, Qt.UserRole)
        if category == "all":
            return
        
        context_menu = QMenu(self)
        
        rename_action = QAction("Đổi tên", self)
        rename_action.triggered.connect(lambda: self.rename_category(category))
        context_menu.addAction(rename_action)
        
        delete_action = QAction("Xóa", self)
        delete_action.triggered.connect(lambda: self.delete_category(category))
        context_menu.addAction(delete_action)
        
        context_menu.exec_(self.category_tree.mapToGlobal(position))
    
    def rename_category(self, old_category):
        """Đổi tên danh mục"""
        if old_category == "Chung":
            QMessageBox.warning(self, 'Cảnh báo', 'Không thể đổi tên danh mục "Chung"!')
            return
        
        new_category, ok = QInputDialog.getText(
            self, 'Đổi tên danh mục', 'Nhập tên mới cho danh mục:',
            text=old_category)
        
        if ok and new_category and new_category != old_category:
            if new_category in self.categories:
                QMessageBox.warning(self, 'Cảnh báo', f'Danh mục "{new_category}" đã tồn tại!')
                return
            
            if self.data_manager.rename_category(old_category, new_category):
                # Cập nhật dữ liệu trong bộ nhớ
                self.vocabulary_sets = self.data_manager.load_all_data()
                self.categories = self.data_manager.get_categories()
                
                # Cập nhật giao diện
                self.update_category_tree()
                self.update_vocab_sets_list()
                
                QMessageBox.information(self, 'Thành công', 
                                      f'Đã đổi tên danh mục "{old_category}" thành "{new_category}"')
            else:
                QMessageBox.critical(self, 'Lỗi', f'Không thể đổi tên danh mục "{old_category}"')
    
    def delete_category(self, category):
        """Xóa danh mục"""
        if category == "Chung":
            QMessageBox.warning(self, 'Cảnh báo', 'Không thể xóa danh mục "Chung"!')
            return
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                    f'Bạn có chắc muốn xóa danh mục "{category}"?\n'
                                    f'Tất cả bộ từ vựng sẽ được chuyển sang danh mục "Chung".',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.data_manager.delete_category(category):
                # Cập nhật dữ liệu trong bộ nhớ
                self.vocabulary_sets = self.data_manager.load_all_data()
                self.categories = self.data_manager.get_categories()
                
                # Cập nhật giao diện
                self.update_category_tree()
                self.update_vocab_sets_list()
                
                QMessageBox.information(self, 'Thành công', 
                                      f'Đã xóa danh mục "{category}" và chuyển các bộ từ vựng sang "Chung"')
            else:
                QMessageBox.critical(self, 'Lỗi', f'Không thể xóa danh mục "{category}"')
    
    def show_vocab_context_menu(self, position):
        """Hiển thị menu ngữ cảnh cho bộ từ vựng"""
        menu = QMenu()
        
        # Chỉ hiển thị menu khi có mục được chọn
        if self.vocab_sets_list.selectedItems():
            selected_item = self.vocab_sets_list.selectedItems()[0]
            # Lấy tên thật của bộ từ vựng từ UserRole
            set_name = selected_item.data(Qt.UserRole)
            
            # Thêm các hành động vào menu
            edit_action = QAction(qta.icon('fa5s.edit', color='#3498db'), "Chỉnh sửa", self)
            edit_action.triggered.connect(lambda: self.edit_vocab_set(set_name))
            
            learn_action = QAction(qta.icon('fa5s.graduation-cap', color='#3498db'), "Học", self)
            learn_action.triggered.connect(lambda: self.start_flashcard(selected_item))
            
            delete_action = QAction(qta.icon('fa5s.trash-alt', color='#e74c3c'), "Xóa", self)
            delete_action.triggered.connect(lambda: self.delete_vocab_set_by_name(set_name))
            
            export_action = QAction(qta.icon('fa5s.file-export', color='#3498db'), "Xuất", self)
            export_action.triggered.connect(lambda: self.export_vocab(selected_item))
            
            # Thêm menu di chuyển
            move_menu = QMenu("Di chuyển đến", menu)
            move_menu.setIcon(qta.icon('fa5s.exchange-alt', color='#3498db'))
            
            # Lấy danh mục hiện tại của bộ từ vựng
            current_category = "Chung"
            if "::" in set_name:
                current_category = set_name.split("::", 1)[0]
            elif set_name in self.vocabulary_sets:
                vocab_data = self.vocabulary_sets[set_name]
                if isinstance(vocab_data, dict) and 'category' in vocab_data:
                    current_category = vocab_data['category']
            
            # Thêm các danh mục vào menu di chuyển
            for category in self.categories:
                if category != current_category:  # Không hiển thị danh mục hiện tại
                    category_action = QAction(category, self)
                    category_action.triggered.connect(lambda checked, c=category: self.move_vocab_set_to_category(set_name, current_category, c))
                    move_menu.addAction(category_action)
            
            # Thêm các hành động vào menu
            menu.addAction(edit_action)
            menu.addAction(learn_action)
            menu.addAction(delete_action)
            menu.addAction(export_action)
            menu.addMenu(move_menu)
            
            # Hiển thị menu tại vị trí chuột
            menu.exec_(self.vocab_sets_list.mapToGlobal(position))
    
    def edit_vocab_set(self, set_name):
        """Chỉnh sửa bộ từ vựng"""
        if set_name in self.vocabulary_sets:
            # Lưu tên bộ từ vựng hiện tại
            self.current_set_name = set_name
            
            # Lấy dữ liệu từ vựng
            vocab_data = self.vocabulary_sets[set_name]
            
            # Đảm bảo category_combo đã được khởi tạo
            if hasattr(self, 'category_combo'):
                # Cập nhật danh sách danh mục
                self.update_category_combo()
                
                # Chọn danh mục
                category = "Chung"  # Mặc định
                if isinstance(vocab_data, dict) and 'category' in vocab_data:
                    category = vocab_data['category']
                
                # Tìm và chọn danh mục trong combobox
                index = self.category_combo.findText(category)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                else:
                    # Nếu không tìm thấy danh mục, thêm vào combobox
                    self.category_combo.addItem(category)
                    self.category_combo.setCurrentText(category)
            
            # Điền thông tin vào form
            self.set_name_edit.setText(set_name)
            
            # Chuyển đổi dữ liệu từ vựng thành văn bản
            vocab_text = ""
            items = []
            if isinstance(vocab_data, list):
                items = vocab_data
            elif isinstance(vocab_data, dict) and 'items' in vocab_data:
                items = vocab_data['items']
            
            for item in items:
                word = item.get('word', '')
                meaning = item.get('meaning', '')
                
                # Định dạng: từ vựng ở một dòng, nghĩa ở dòng tiếp theo, sau đó là dòng trống
                vocab_text += f"{word}\n{meaning}\n\n"
            
            self.vocab_edit.setText(vocab_text.strip())
            
            # Chuyển đến trang chỉnh sửa
            self.stacked_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, 'Cảnh báo', f'Không tìm thấy bộ từ vựng "{set_name}"!')
    
    def move_vocab_set_to_category(self, set_name, old_category, new_category):
        """Di chuyển bộ từ vựng sang danh mục khác"""
        # Xác định tên thực của bộ từ vựng (không có tiền tố danh mục)
        actual_set_name = set_name
        if "::" in set_name:
            old_category, actual_set_name = set_name.split("::", 1)
        
        # Kiểm tra xem bộ từ vựng đã tồn tại trong danh mục đích chưa
        if self.data_manager.check_vocab_set_exists(actual_set_name, new_category):
            reply = QMessageBox.question(self, 'Xác nhận', 
                                        f'Bộ từ vựng "{actual_set_name}" đã tồn tại trong danh mục "{new_category}". Bạn có muốn ghi đè không?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        # Di chuyển bộ từ vựng
        if self.data_manager.move_vocab_set(actual_set_name, old_category, new_category):
            # Cập nhật dữ liệu trong bộ nhớ
            self.vocabulary_sets = self.data_manager.load_all_data()
            self.update_vocab_sets_list()
            QMessageBox.information(self, 'Thành công', 
                                  f'Đã di chuyển bộ từ vựng "{actual_set_name}" từ danh mục "{old_category}" sang "{new_category}"')
        else:
            QMessageBox.critical(self, 'Lỗi', 
                               f'Không thể di chuyển bộ từ vựng "{actual_set_name}" sang danh mục "{new_category}"')
    
    def export_vocab(self, item=None):
        """Xuất bộ từ vựng ra file"""
        # Nếu không có item được truyền vào, lấy item đang được chọn
        if item is None:
            selected_items = self.vocab_sets_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng chọn một bộ từ vựng để xuất!')
                return
            item = selected_items[0]
        
        # Lấy tên thật của bộ từ vựng từ UserRole
        set_name = item.data(Qt.UserRole)
        
        # Tìm bộ từ vựng trong dữ liệu
        if set_name in self.vocabulary_sets:
            vocab_data = self.vocabulary_sets[set_name]
            
            # Hiển thị hộp thoại lưu file
            file_path, _ = QFileDialog.getSaveFileName(self, "Lưu bộ từ vựng", 
                                                    f"{set_name}.json", 
                                                    "JSON Files (*.json)")
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump({set_name: vocab_data}, f, 
                                ensure_ascii=False, indent=2)
                    QMessageBox.information(self, 'Thành công', f'Đã xuất bộ từ vựng "{set_name}" thành công!')
                except Exception as e:
                    QMessageBox.critical(self, 'Lỗi', f'Lỗi khi xuất file: {str(e)}')
        else:
            QMessageBox.warning(self, 'Cảnh báo', f'Không tìm thấy bộ từ vựng "{set_name}" trong dữ liệu!')
    
    def start_flashcard_for_set(self, set_name):
        """Bắt đầu học từ vựng với flashcard cho bộ từ vựng cụ thể"""
        if set_name in self.vocabulary_sets:
            vocab_data = self.vocabulary_sets[set_name]
            
            # Xác định danh sách từ vựng
            if isinstance(vocab_data, list):
                vocab_items = vocab_data
            elif isinstance(vocab_data, dict) and 'items' in vocab_data:
                vocab_items = vocab_data['items']
            else:
                QMessageBox.warning(self, 'Cảnh báo', 'Định dạng bộ từ vựng không hợp lệ!')
                return
            
            # Xóa widget flashcard cũ nếu có
            if hasattr(self, 'flashcard_widget'):
                self.flashcard_widget.deleteLater()
            
            # Lấy tên hiển thị của bộ từ vựng (loại bỏ tiền tố danh mục nếu có)
            display_name = set_name
            if "::" in set_name:
                _, display_name = set_name.split("::", 1)
            
            # Tạo widget flashcard mới với tên bộ từ vựng
            self.flashcard_widget = FlashcardWidget(vocab_items, set_name=display_name)
            
            # Kết nối tín hiệu back_to_main với phương thức switch_to_main_page
            self.flashcard_widget.back_to_main.connect(self.switch_to_main_page)
            
            # Thêm widget vào trang flashcard
            flashcard_layout = QVBoxLayout()
            flashcard_layout.addWidget(self.flashcard_widget)
            
            # Xóa layout cũ nếu có
            if self.flashcard_page.layout():
                QWidget().setLayout(self.flashcard_page.layout())
            
            # Thiết lập layout mới
            self.flashcard_page.setLayout(flashcard_layout)
            
            # Chuyển đến trang flashcard
            self.stacked_widget.setCurrentWidget(self.flashcard_page)
    
    def start_flashcard(self, item):
        """Bắt đầu học từ vựng với flashcard"""
        # Lấy tên thật của bộ từ vựng từ UserRole
        set_name = item.data(Qt.UserRole)
        self.start_flashcard_for_set(set_name)
    
    def switch_to_main_page(self):
        """Chuyển về trang chính"""
        self.stacked_widget.setCurrentIndex(0)
        self.update_vocab_sets_list()
    
    def create_new_set(self):
        """Tạo bộ từ vựng mới"""
        self.set_name_edit.clear()
        self.vocab_edit.clear()
        self.category_combo.setCurrentIndex(0)
        self.stacked_widget.setCurrentIndex(1)
    
    def add_vocabulary(self):
        """Thêm hoặc cập nhật bộ từ vựng"""
        set_name = self.set_name_edit.text().strip()
        if not set_name:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng nhập tên bộ từ vựng!')
            return
        
        # Lấy danh mục đã chọn
        category_index = self.category_combo.currentIndex()
        if category_index <= 0:  # "Không có danh mục" hoặc không chọn
            category = "Chung"
        else:
            category = self.category_combo.currentText()
        
        # Lấy nội dung từ vựng và chuyển đổi thành văn bản thuần túy
        vocab_text = self.vocab_edit.toPlainText().strip()
        
        # Kiểm tra nếu nội dung rỗng
        if not vocab_text:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng nhập nội dung từ vựng!')
            return
        
        # Phân tích văn bản từ vựng
        from utils.vocab_parser import VocabParser
        parser = VocabParser()
        vocab_items = parser.parse_vocab_text(vocab_text)
        
        # Kiểm tra nếu không có từ vựng nào được phân tích
        if not vocab_items:
            QMessageBox.warning(self, 'Cảnh báo', 'Không thể phân tích nội dung từ vựng. Vui lòng kiểm tra định dạng!')
            return
        
        # Đếm số từ mới được thêm vào
        num_new_words = len(vocab_items)
        
        # Tạo dữ liệu từ vựng
        vocab_data = {
            'category': category,
            'items': vocab_items
        }
        
        # Lưu bộ từ vựng
        old_name = self.current_set_name
        if old_name and old_name != set_name:
            # Đổi tên bộ từ vựng
            self.data_manager.delete_vocab_set(old_name)
        
        self.data_manager.save_vocab_set(set_name, vocab_data, category)
        
        # Cập nhật dữ liệu trong bộ nhớ
        self.vocabulary_sets = self.data_manager.load_all_data()
        self.update_vocab_sets_list()
        
        # Hiển thị thông báo thành công với số từ mới
        QMessageBox.information(self, 'Thành công', 
                               f'Đã lưu bộ từ vựng "{set_name}" với {num_new_words} từ!')
        
        # Quay lại trang chính
        self.switch_to_main_page()
    
    def delete_vocab_set_by_name(self, set_name):
        reply = QMessageBox.question(self, 'Xác nhận', 
                                    f'Bạn có chắc muốn xóa bộ từ vựng "{set_name}"?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Kiểm tra xem set_name có phải là khóa đầy đủ không (có dạng "category::name")
            if set_name in self.vocabulary_sets:
                # Trường hợp set_name chính là khóa đầy đủ
                if "::" in set_name:
                    category, actual_set_name = set_name.split("::", 1)
                else:
                    category = "Chung"
                    actual_set_name = set_name
                
                print(f"Xóa bộ từ vựng: category={category}, name={actual_set_name}")
                
                if self.data_manager.delete_vocab_set(actual_set_name, category):
                    del self.vocabulary_sets[set_name]
                    self.update_vocab_sets_list()
                    QMessageBox.information(self, 'Thành công', f'Đã xóa bộ từ vựng "{set_name}"')
                else:
                    QMessageBox.critical(self, 'Lỗi', f'Không thể xóa file bộ từ vựng "{set_name}"')
            else:
                # Trường hợp set_name không phải là khóa đầy đủ
                found = False
                for key in list(self.vocabulary_sets.keys()):
                    if key.endswith(f"::{set_name}"):
                        category = key.split("::", 1)[0]
                        if self.data_manager.delete_vocab_set(set_name, category):
                            del self.vocabulary_sets[key]
                            found = True
                            break
                
                if found:
                    self.update_vocab_sets_list()
                    QMessageBox.information(self, 'Thành công', f'Đã xóa bộ từ vựng "{set_name}"')
                else:
                    # Thử xóa từ tất cả các danh mục
                    for category in self.categories:
                        if self.data_manager.delete_vocab_set(set_name, category):
                            self.vocabulary_sets = self.data_manager.load_all_data()
                            self.update_vocab_sets_list()
                            QMessageBox.information(self, 'Thành công', f'Đã xóa bộ từ vựng "{set_name}"')
                            return
                    
                    QMessageBox.critical(self, 'Lỗi', f'Không tìm thấy bộ từ vựng "{set_name}" trong dữ liệu')
    
    def import_vocab(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file từ vựng", 
                                                "", "JSON Files (*.json);;Text Files (*.txt)")
        
        if file_path:
            try:
                total_words_imported = 0
                sets_imported = 0
                
                if file_path.endswith('.json'):
                    # Nhập từ file JSON
                    with open(file_path, 'r', encoding='utf-8') as f:
                        imported_data = json.load(f)
                    
                    category = "Chung"  # Danh mục mặc định
                    
                    for set_name, vocab_data in imported_data.items():
                        if set_name in self.vocabulary_sets:
                            reply = QMessageBox.question(self, 'Xác nhận', 
                                                f'Bộ từ vựng "{set_name}" đã tồn tại. Bạn có muốn ghi đè không?',
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            
                            if reply == QMessageBox.No:
                                continue
                        
                        # Lưu bộ từ vựng
                        if isinstance(vocab_data, dict) and 'category' in vocab_data:
                            category = vocab_data['category']
                        
                        # Đếm số từ trong bộ từ vựng
                        num_words = 0
                        if isinstance(vocab_data, list):
                            num_words = len(vocab_data)
                        elif isinstance(vocab_data, dict) and 'items' in vocab_data:
                            num_words = len(vocab_data['items'])
                        
                        self.data_manager.save_vocab_set(set_name, vocab_data, category)
                        total_words_imported += num_words
                        sets_imported += 1
                
                elif file_path.endswith('.txt'):
                    # Nhập từ file văn bản
                    with open(file_path, 'r', encoding='utf-8') as f:
                        vocab_text = f.read().strip()
                    
                    # Lấy tên file làm tên bộ từ vựng
                    set_name = os.path.splitext(os.path.basename(file_path))[0]
                    
                    # Phân tích văn bản từ vựng
                    from utils.vocab_parser import VocabParser
                    parser = VocabParser()
                    vocab_items = parser.parse_vocab_text(vocab_text)
                    
                    # Kiểm tra nếu không có từ vựng nào được phân tích
                    if not vocab_items:
                        QMessageBox.warning(self, 'Cảnh báo', 'Không thể phân tích nội dung từ vựng. Vui lòng kiểm tra định dạng!')
                        return
                    
                    # Tạo dữ liệu từ vựng
                    vocab_data = {
                        'category': "Chung",
                        'items': vocab_items
                    }
                    
                    # Kiểm tra nếu bộ từ vựng đã tồn tại
                    if set_name in self.vocabulary_sets:
                        reply = QMessageBox.question(self, 'Xác nhận', 
                                            f'Bộ từ vựng "{set_name}" đã tồn tại. Bạn có muốn ghi đè không?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        
                        if reply == QMessageBox.No:
                            return
                    
                    # Lưu bộ từ vựng
                    self.data_manager.save_vocab_set(set_name, vocab_data, "Chung")
                    total_words_imported += len(vocab_items)
                    sets_imported += 1
                
                # Cập nhật dữ liệu trong bộ nhớ
                self.vocabulary_sets = self.data_manager.load_all_data()
                self.update_vocab_sets_list()
                
                # Hiển thị thông báo thành công với số từ mới
                QMessageBox.information(self, 'Thành công', 
                                       f'Đã nhập {sets_imported} bộ từ vựng với tổng cộng {total_words_imported} từ!')
            
            except Exception as e:
                QMessageBox.critical(self, 'Lỗi', f'Lỗi khi nhập file: {str(e)}')
    
    def closeEvent(self, event):
        # Không cần lưu dữ liệu vì mỗi thay đổi đã được lưu ngay lập tức
        event.accept()

    def load_categories(self):
        """Tải danh sách danh mục từ data_manager"""
        try:
            return self.data_manager.get_categories()
        except Exception as e:
            print(f"Lỗi khi tải danh mục: {str(e)}")
            return ["Chung"]  # Trả về danh mục mặc định nếu có lỗi 
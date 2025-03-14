import os
import json
import shutil
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTextEdit, QPushButton, QLineEdit, 
                            QMessageBox, QListWidget, QListWidgetItem, QFileDialog, QStackedWidget,
                            QToolButton, QSizePolicy, QFrame, QSpacerItem,
                            QTreeWidget, QTreeWidgetItem, QSplitter, QComboBox,
                            QInputDialog, QMenu, QAction)
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
        # Thiết lập cửa sổ chính
        self.setWindowTitle('FlashLearnVN')
        self.setGeometry(100, 100, 400, 300)  # Giảm chiều cao xuống 300
        
        # Sử dụng logo từ file nếu tồn tại, nếu không thì sử dụng qtawesome
        logo_path = "ui/images/logo.ico"
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        else:
            self.setWindowIcon(QIcon(qta.icon('fa5s.book-open', color='#3498db').pixmap(64, 64)))
        
        # Widget trung tâm với StackedWidget để chuyển đổi giữa các trang
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout chính
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # StackedWidget để chứa các trang
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Trang 1: Danh sách bộ từ vựng
        self.main_page = QWidget()
        self.setup_main_page()
        self.stacked_widget.addWidget(self.main_page)
        
        # Trang 2: Thêm/Chỉnh sửa từ vựng
        self.edit_page = QWidget()
        self.setup_edit_page()
        self.stacked_widget.addWidget(self.edit_page)
        
        # Trang 3: Học từ vựng (Flashcard)
        self.flashcard_page = QWidget()
        self.stacked_widget.addWidget(self.flashcard_page)
        
        # Hiển thị trang chính
        self.stacked_widget.setCurrentIndex(0)
        
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
        left_panel.setMaximumWidth(130)  # Giảm chiều rộng
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
        """Thiết lập trang chỉnh sửa từ vựng"""
        layout = QVBoxLayout(self.edit_page)
        layout.setSpacing(5)  # Giảm khoảng cách
        layout.setContentsMargins(5, 5, 5, 5)  # Giảm margin
        
        # Tiêu đề
        title_label = QLabel("Thêm/Chỉnh sửa bộ từ vựng")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 2px 0;")
        layout.addWidget(title_label)
        
        # Form nhập liệu
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(5)  # Giảm khoảng cách
        form_layout.setContentsMargins(5, 5, 5, 5)  # Giảm margin
        
        # Tên bộ từ vựng
        name_layout = QHBoxLayout()
        name_label = QLabel("Tên bộ từ vựng:")
        name_label.setFont(QFont("Segoe UI", 9))
        name_layout.addWidget(name_label)
        
        self.set_name_edit = QLineEdit()
        self.set_name_edit.setPlaceholderText("Nhập tên bộ từ vựng")
        self.set_name_edit.setFont(QFont("Segoe UI", 9))
        name_layout.addWidget(self.set_name_edit)
        
        form_layout.addLayout(name_layout)
        
        # Danh mục
        category_layout = QHBoxLayout()
        category_label = QLabel("Danh mục:")
        category_label.setFont(QFont("Segoe UI", 9))
        category_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont("Segoe UI", 9))
        category_layout.addWidget(self.category_combo)
        
        form_layout.addLayout(category_layout)
        
        # Hướng dẫn
        instruction_label = QLabel(
            "Nhập từ vựng theo định dạng sau:\n"
            "word (type):\n"
            "/pronunciation/ meaning\n\n"
            "Ví dụ có phiên âm:\n"
            "hello (n):\n"
            "/həˈləʊ/ xin chào\n\n"
        )
        instruction_label.setStyleSheet("color: #7f8c8d; background-color: #f8f9fa; padding: 3px; border-radius: 3px; font-size: 8px;")
        form_layout.addWidget(instruction_label)
        
        # Nội dung từ vựng
        vocab_label = QLabel("Nội dung từ vựng:")
        vocab_label.setFont(QFont("Segoe UI", 9))
        form_layout.addWidget(vocab_label)
        
        self.vocab_edit = QTextEdit()
        self.vocab_edit.setPlaceholderText("Nhập từ vựng ở đây...")
        self.vocab_edit.setFont(QFont("Segoe UI", 9))
        self.vocab_edit.setMinimumHeight(80)  # Giảm chiều cao tối thiểu
        self.vocab_edit.setMaximumHeight(100)  # Giới hạn chiều cao tối đa
        form_layout.addWidget(self.vocab_edit)
        
        layout.addWidget(form_frame)
        
        # Các nút thao tác
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)  # Giảm khoảng cách
        
        # Nút hủy
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setIcon(qta.icon('fa5s.times', color='white'))
        self.cancel_button.clicked.connect(self.switch_to_main_page)
        buttons_layout.addWidget(self.cancel_button)
        
        # Nút lưu
        self.save_button = QPushButton("Lưu")
        self.save_button.setIcon(qta.icon('fa5s.save', color='white'))
        self.save_button.clicked.connect(self.add_vocabulary)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
    
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
        
        # Thêm mục "Tất cả"
        all_item = QTreeWidgetItem(self.category_tree, ["Tất cả"])
        all_item.setIcon(0, qta.icon('fa5s.list', color='#3498db'))
        all_item.setData(0, Qt.UserRole, "all")
        
        # Thêm các danh mục
        for category in self.categories:
            cat_item = QTreeWidgetItem(self.category_tree, [category])
            cat_item.setIcon(0, qta.icon('fa5s.folder', color='#f39c12'))
            cat_item.setData(0, Qt.UserRole, category)
        
        # Mở rộng tất cả các mục
        self.category_tree.expandAll()
        
        # Cập nhật danh mục trong combobox
        self.update_category_combo()
    
    def update_category_combo(self):
        """Cập nhật combobox danh mục"""
        if hasattr(self, 'category_combo'):
            self.category_combo.clear()
            self.category_combo.addItem("Không có danh mục")
            for category in self.categories:
                self.category_combo.addItem(category)
    
    def update_vocab_sets_list(self, category=None):
        """Cập nhật danh sách bộ từ vựng theo danh mục"""
        self.vocab_sets_list.clear()
        
        if category is None or category == "all":
            # Hiển thị tất cả bộ từ vựng
            for set_name, vocab_set in self.vocabulary_sets.items():
                item = QListWidgetItem(set_name)
                item.setIcon(qta.icon('fa5s.book', color='#3498db'))
                self.vocab_sets_list.addItem(item)
            self.vocab_title.setText("Tất cả bộ từ vựng")
        else:
            # Hiển thị bộ từ vựng theo danh mục
            for set_name, vocab_set in self.vocabulary_sets.items():
                if 'category' in vocab_set and vocab_set['category'] == category:
                    item = QListWidgetItem(set_name)
                    item.setIcon(qta.icon('fa5s.book', color='#3498db'))
                    self.vocab_sets_list.addItem(item)
            self.vocab_title.setText(f"Bộ từ vựng - {category}")
    
    def category_selected(self, item):
        """Xử lý khi chọn danh mục"""
        category = item.data(0, Qt.UserRole)
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
            set_name = selected_item.text()
            
            # Thêm các hành động vào menu
            edit_action = QAction(qta.icon('fa5s.edit', color='#3498db'), "Chỉnh sửa", self)
            edit_action.triggered.connect(lambda: self.edit_vocab_set(set_name))
            
            learn_action = QAction(qta.icon('fa5s.graduation-cap', color='#3498db'), "Học", self)
            learn_action.triggered.connect(lambda: self.start_flashcard(selected_item))
            
            delete_action = QAction(qta.icon('fa5s.trash-alt', color='#e74c3c'), "Xóa", self)
            delete_action.triggered.connect(lambda: self.delete_vocab_set_by_name(set_name))
            
            export_action = QAction(qta.icon('fa5s.file-export', color='#3498db'), "Xuất", self)
            export_action.triggered.connect(self.export_vocab)
            
            # Thêm các hành động vào menu
            menu.addAction(edit_action)
            menu.addAction(learn_action)
            menu.addAction(delete_action)
            menu.addAction(export_action)
            
            # Hiển thị menu tại vị trí chuột
            menu.exec_(self.vocab_sets_list.mapToGlobal(position))
    
    def edit_vocab_set(self, set_name):
        """Chỉnh sửa bộ từ vựng"""
        if set_name in self.vocabulary_sets:
            # Lưu tên bộ từ vựng hiện tại
            self.current_set_name = set_name
            
            # Lấy dữ liệu từ vựng
            vocab_data = self.vocabulary_sets[set_name]
            
            # Cập nhật danh sách danh mục
            self.update_category_combo()
            
            # Điền thông tin vào form
            self.set_name_edit.setText(set_name)
            
            # Chọn danh mục
            if isinstance(vocab_data, dict) and 'category' in vocab_data:
                category = vocab_data['category']
                index = self.category_combo.findText(category)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
            
            # Chuyển đổi dữ liệu từ vựng thành văn bản
            vocab_text = ""
            items = []
            if isinstance(vocab_data, list):
                items = vocab_data
            elif isinstance(vocab_data, dict) and 'items' in vocab_data:
                items = vocab_data['items']
            
            for item in items:
                word = item.get('word', '')
                word_type = item.get('type', '')
                pronunciation = item.get('pronunciation', '')
                meaning = item.get('meaning', '')
                
                # Định dạng theo yêu cầu mới
                if word_type:
                    vocab_text += f"{word} ({word_type}):\n"
                else:
                    vocab_text += f"{word}:\n"
                
                # Nếu có phiên âm thì hiển thị, nếu không thì chỉ hiển thị nghĩa
                if pronunciation and pronunciation.strip():
                    vocab_text += f"{pronunciation} {meaning}\n\n"
                else:
                    vocab_text += f"{meaning}\n\n"
            
            self.vocab_edit.setText(vocab_text.strip())
            
            # Chuyển đến trang chỉnh sửa
            self.stacked_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, 'Cảnh báo', f'Không tìm thấy bộ từ vựng "{set_name}"!')
    
    def move_to_category(self, set_name, category):
        """Chuyển bộ từ vựng đến danh mục khác"""
        if set_name in self.vocabulary_sets:
            # Nếu category là None, xóa thuộc tính category
            if category is None:
                if 'category' in self.vocabulary_sets[set_name]:
                    self.vocabulary_sets[set_name].pop('category')
            else:
                # Đảm bảo vocabulary_sets[set_name] là dict
                if not isinstance(self.vocabulary_sets[set_name], dict):
                    # Chuyển đổi từ list sang dict
                    items = self.vocabulary_sets[set_name]
                    self.vocabulary_sets[set_name] = {'items': items, 'category': category}
                else:
                    self.vocabulary_sets[set_name]['category'] = category
            
            # Lưu thay đổi
            self.data_manager.save_data(self.vocabulary_sets)
            
            # Cập nhật giao diện
            current_item = self.category_tree.currentItem()
            if current_item:
                current_category = current_item.data(0, Qt.UserRole)
                self.update_vocab_sets_list(current_category)
    
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
            
            # Tạo widget flashcard mới
            self.flashcard_widget = FlashcardWidget(vocab_items)
            
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
        set_name = item.text()
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
        from utils.vocab_parser import VocabParser
        
        set_name = self.set_name_edit.text().strip()
        if not set_name:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng nhập tên bộ từ vựng!')
            return
        
        vocab_text = self.vocab_edit.toPlainText().strip()
        if not vocab_text:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng nhập từ vựng!')
            return
        
        # Lấy danh mục đã chọn
        category = self.category_combo.currentText()
        if not category:
            category = "Chung"
        
        # Phân tích văn bản từ vựng
        parser = VocabParser()
        vocab_items = parser.parse_vocab_text(vocab_text)
        
        if not vocab_items:
            QMessageBox.warning(self, 'Cảnh báo', 'Không thể phân tích từ vựng. Vui lòng kiểm tra định dạng!')
            return
        
        # Chuẩn bị dữ liệu để lưu
        vocab_data = {
            'items': vocab_items,
            'category': category
        }
        
        # Lưu bộ từ vựng
        if self.data_manager.save_vocab_set(set_name, vocab_data, category):
            # Cập nhật dữ liệu trong bộ nhớ
            self.vocabulary_sets[set_name] = vocab_data
            
            QMessageBox.information(self, 'Thành công', 
                                  f'Đã lưu {len(vocab_items)} từ vào bộ từ vựng "{set_name}" trong danh mục "{category}"')
            self.switch_to_main_page()  # Quay lại trang chính
        else:
            QMessageBox.critical(self, 'Lỗi', f'Không thể lưu bộ từ vựng "{set_name}"')
    
    def delete_vocab_set_by_name(self, set_name):
        reply = QMessageBox.question(self, 'Xác nhận', 
                                    f'Bạn có chắc muốn xóa bộ từ vựng "{set_name}"?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if set_name in self.vocabulary_sets:
                # Lấy danh mục của bộ từ vựng
                category = "Chung"
                if isinstance(self.vocabulary_sets[set_name], dict) and 'category' in self.vocabulary_sets[set_name]:
                    category = self.vocabulary_sets[set_name]['category']
                
                # Xóa file
                if self.data_manager.delete_vocab_set(set_name, category):
                    # Xóa khỏi bộ nhớ
                    del self.vocabulary_sets[set_name]
                    self.update_vocab_sets_list()
                    QMessageBox.information(self, 'Thành công', f'Đã xóa bộ từ vựng "{set_name}"')
                else:
                    QMessageBox.critical(self, 'Lỗi', f'Không thể xóa bộ từ vựng "{set_name}"')
    
    def export_vocab(self):
        selected_items = self.vocab_sets_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng chọn một bộ từ vựng để xuất!')
            return
        
        set_name = selected_items[0].text()
        if set_name in self.vocabulary_sets:
            file_path, _ = QFileDialog.getSaveFileName(self, "Lưu bộ từ vựng", 
                                                    f"{set_name}.json", 
                                                    "JSON Files (*.json)")
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump({set_name: self.vocabulary_sets[set_name]}, f, 
                                ensure_ascii=False, indent=2)
                    QMessageBox.information(self, 'Thành công', f'Đã xuất bộ từ vựng "{set_name}" thành công!')
                except Exception as e:
                    QMessageBox.critical(self, 'Lỗi', f'Lỗi khi xuất file: {str(e)}')
    
    def import_vocab(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file từ vựng", 
                                                "", "JSON Files (*.json)")
        
        if file_path:
            try:
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
                    
                    self.data_manager.save_vocab_set(set_name, vocab_data, category)
                
                # Cập nhật dữ liệu trong bộ nhớ
                self.vocabulary_sets = self.data_manager.load_all_data()
                self.update_vocab_sets_list()
                QMessageBox.information(self, 'Thành công', 'Đã nhập từ vựng thành công!')
            
            except Exception as e:
                QMessageBox.critical(self, 'Lỗi', f'Lỗi khi nhập file: {str(e)}')
    
    def closeEvent(self, event):
        # Không cần lưu dữ liệu vì mỗi thay đổi đã được lưu ngay lập tức
        event.accept()

    def load_categories(self):
        """Tải danh sách các danh mục"""
        return self.data_manager.get_categories() 
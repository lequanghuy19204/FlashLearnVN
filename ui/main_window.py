import os
import json
import shutil
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTextEdit, QPushButton, QLineEdit, 
                            QMessageBox, QListWidget, QFileDialog, QStackedWidget,
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
        self.data_manager = DataManager("data/vocabulary_data.json")
        self.vocabulary_sets = self.data_manager.load_data()
        self.current_set_name = ""
        self.categories = self.load_categories()
        self.initUI()
        
    def initUI(self):
        # Thiết lập cửa sổ chính
        self.setWindowTitle('FlashLearnVN - Ứng dụng Học Từ Vựng')
        self.setGeometry(100, 100, 1200, 800)
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
        
        # Thanh tiêu đề
        header = QFrame()
        header.setStyleSheet("background-color: #3498db; color: white;")
        header.setMinimumHeight(80)
        header_layout = QHBoxLayout(header)
        
        # Logo và tiêu đề
        logo_label = QLabel()
        logo_label.setPixmap(qta.icon('fa5s.book-open', color='white').pixmap(48, 48))
        header_layout.addWidget(logo_label)
        
        title_label = QLabel("FlashLearnVN")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Thêm header vào layout chính
        layout.addWidget(header)
        
        # Nội dung chính
        content = QSplitter(Qt.Horizontal)
        
        # Panel bên trái - Danh mục
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #f8f9fa;")
        left_panel.setMaximumWidth(300)
        left_panel_layout = QVBoxLayout(left_panel)
        
        # Tiêu đề danh mục
        category_header = QFrame()
        category_header.setStyleSheet("background-color: #e9ecef;")
        category_header_layout = QHBoxLayout(category_header)
        
        category_title = QLabel("Danh mục")
        category_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        category_header_layout.addWidget(category_title)
        
        # Nút thêm danh mục
        add_category_btn = QToolButton()
        add_category_btn.setIcon(qta.icon('fa5s.plus', color='#3498db'))
        add_category_btn.setToolTip("Thêm danh mục mới")
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
                height: 30px;
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
        
        # Tiêu đề bộ từ vựng
        vocab_header = QFrame()
        vocab_header.setStyleSheet("background-color: #e9ecef;")
        vocab_header_layout = QHBoxLayout(vocab_header)
        
        self.vocab_title = QLabel("Tất cả bộ từ vựng")
        self.vocab_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        vocab_header_layout.addWidget(self.vocab_title)
        
        # Nút thêm bộ từ vựng
        add_vocab_btn = QToolButton()
        add_vocab_btn.setIcon(qta.icon('fa5s.plus', color='#3498db'))
        add_vocab_btn.setToolTip("Thêm bộ từ vựng mới")
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
                height: 40px;
                border-bottom: 1px solid #f1f2f6;
                padding: 8px;
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
        content.setSizes([300, 900])  # Thiết lập kích thước ban đầu
        
        # Thêm nội dung vào layout chính
        layout.addWidget(content)
        
        # Thanh trạng thái
        status_bar = QFrame()
        status_bar.setStyleSheet("background-color: #e9ecef;")
        status_bar.setMinimumHeight(30)
        status_bar_layout = QHBoxLayout(status_bar)
        status_bar_layout.setContentsMargins(10, 0, 10, 0)
        
        status_label = QLabel("Sẵn sàng")
        status_bar_layout.addWidget(status_label)
        
        layout.addWidget(status_bar)
        
        # Cập nhật danh sách danh mục và bộ từ vựng
        self.update_category_tree()
        self.update_vocab_sets_list()
    
    def setup_edit_page(self):
        """Thiết lập trang chỉnh sửa từ vựng"""
        layout = QVBoxLayout(self.edit_page)
        layout.setSpacing(15)
        
        # Tiêu đề
        title_label = QLabel("Thêm/Chỉnh sửa bộ từ vựng")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        layout.addWidget(title_label)
        
        # Form nhập liệu
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Tên bộ từ vựng
        name_layout = QHBoxLayout()
        name_label = QLabel("Tên bộ từ vựng:")
        name_label.setFont(QFont("Segoe UI", 12))
        name_layout.addWidget(name_label)
        
        self.set_name_edit = QLineEdit()
        self.set_name_edit.setPlaceholderText("Nhập tên bộ từ vựng")
        self.set_name_edit.setFont(QFont("Segoe UI", 12))
        name_layout.addWidget(self.set_name_edit)
        
        form_layout.addLayout(name_layout)
        
        # Danh mục
        category_layout = QHBoxLayout()
        category_label = QLabel("Danh mục:")
        category_label.setFont(QFont("Segoe UI", 12))
        category_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont("Segoe UI", 12))
        category_layout.addWidget(self.category_combo)
        
        form_layout.addLayout(category_layout)
        
        # Hướng dẫn
        instruction_label = QLabel(
            "Nhập từ vựng theo định dạng sau:\n"
            "word (type): pronunciation meaning\n"
            "Ví dụ: hello (n): /həˈləʊ/ xin chào"
        )
        instruction_label.setStyleSheet("color: #7f8c8d; background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        form_layout.addWidget(instruction_label)
        
        # Nội dung từ vựng
        vocab_label = QLabel("Nội dung từ vựng:")
        vocab_label.setFont(QFont("Segoe UI", 12))
        form_layout.addWidget(vocab_label)
        
        self.vocab_edit = QTextEdit()
        self.vocab_edit.setPlaceholderText("Nhập từ vựng ở đây...")
        self.vocab_edit.setFont(QFont("Segoe UI", 12))
        self.vocab_edit.setMinimumHeight(300)
        form_layout.addWidget(self.vocab_edit)
        
        layout.addWidget(form_frame)
        
        # Các nút thao tác
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
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
                item = QListWidget.QListWidgetItem(set_name)
                item.setIcon(qta.icon('fa5s.book', color='#3498db'))
                self.vocab_sets_list.addItem(item)
            self.vocab_title.setText("Tất cả bộ từ vựng")
        else:
            # Hiển thị bộ từ vựng theo danh mục
            for set_name, vocab_set in self.vocabulary_sets.items():
                if 'category' in vocab_set and vocab_set['category'] == category:
                    item = QListWidget.QListWidgetItem(set_name)
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
            
            self.categories.append(category_name)
            self.save_categories()
            self.update_category_tree()
    
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
    
    def rename_category(self, category):
        """Đổi tên danh mục"""
        new_name, ok = QInputDialog.getText(
            self, 'Đổi tên danh mục', 'Nhập tên mới:', text=category)
        
        if ok and new_name and new_name != category:
            if new_name in self.categories:
                QMessageBox.warning(self, 'Cảnh báo', 'Danh mục này đã tồn tại!')
                return
            
            # Cập nhật tên danh mục trong danh sách
            index = self.categories.index(category)
            self.categories[index] = new_name
            
            # Cập nhật danh mục trong các bộ từ vựng
            for set_name, vocab_set in self.vocabulary_sets.items():
                if 'category' in vocab_set and vocab_set['category'] == category:
                    vocab_set['category'] = new_name
            
            # Lưu thay đổi
            self.save_categories()
            self.data_manager.save_data(self.vocabulary_sets)
            
            # Cập nhật giao diện
            self.update_category_tree()
            self.update_vocab_sets_list()
    
    def delete_category(self, category):
        """Xóa danh mục"""
        reply = QMessageBox.question(
            self, 'Xác nhận', 
            f'Bạn có chắc muốn xóa danh mục "{category}"?\n'
            'Các bộ từ vựng trong danh mục này sẽ không bị xóa.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Xóa danh mục khỏi danh sách
            self.categories.remove(category)
            
            # Xóa danh mục trong các bộ từ vựng
            for set_name, vocab_set in self.vocabulary_sets.items():
                if 'category' in vocab_set and vocab_set['category'] == category:
                    vocab_set.pop('category', None)
            
            # Lưu thay đổi
            self.save_categories()
            self.data_manager.save_data(self.vocabulary_sets)
            
            # Cập nhật giao diện
            self.update_category_tree()
            self.update_vocab_sets_list()
    
    def show_vocab_context_menu(self, position):
        """Hiển thị menu ngữ cảnh cho bộ từ vựng"""
        item = self.vocab_sets_list.itemAt(position)
        if not item:
            return
        
        set_name = item.text()
        
        context_menu = QMenu(self)
        
        study_action = QAction("Học", self)
        study_action.triggered.connect(lambda: self.start_flashcard_for_set(set_name))
        context_menu.addAction(study_action)
        
        edit_action = QAction("Chỉnh sửa", self)
        edit_action.triggered.connect(lambda: self.edit_vocab_set_by_name(set_name))
        context_menu.addAction(edit_action)
        
        move_menu = QMenu("Chuyển đến danh mục", self)
        
        # Thêm tùy chọn "Không có danh mục"
        no_category_action = QAction("Không có danh mục", self)
        no_category_action.triggered.connect(lambda: self.move_to_category(set_name, None))
        move_menu.addAction(no_category_action)
        
        # Thêm các danh mục
        for category in self.categories:
            category_action = QAction(category, self)
            category_action.triggered.connect(lambda checked, cat=category: self.move_to_category(set_name, cat))
            move_menu.addAction(category_action)
        
        context_menu.addMenu(move_menu)
        
        delete_action = QAction("Xóa", self)
        delete_action.triggered.connect(lambda: self.delete_vocab_set_by_name(set_name))
        context_menu.addAction(delete_action)
        
        context_menu.exec_(self.vocab_sets_list.mapToGlobal(position))
    
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
    
    def start_flashcard(self):
        """Bắt đầu học từ vựng với flashcard"""
        selected_items = self.vocab_sets_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng chọn một bộ từ vựng để học!')
            return
        
        set_name = selected_items[0].text()
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
    
    def edit_vocab_set_by_name(self, set_name):
        """Chỉnh sửa bộ từ vựng theo tên"""
        if set_name in self.vocabulary_sets:
            vocab_data = self.vocabulary_sets[set_name]
            
            # Xác định danh sách từ vựng và danh mục
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
        
        # Phân tích văn bản từ vựng
        parser = VocabParser()
        vocab_items = parser.parse_vocab_text(vocab_text)
        
        if not vocab_items:
            QMessageBox.warning(self, 'Cảnh báo', 'Không thể phân tích từ vựng. Vui lòng kiểm tra định dạng!')
            return
        
        # Lưu bộ từ vựng
        self.vocabulary_sets[set_name] = vocab_items
        self.data_manager.save_data(self.vocabulary_sets)
        
        QMessageBox.information(self, 'Thành công', f'Đã lưu {len(vocab_items)} từ vào bộ từ vựng "{set_name}"')
        self.switch_to_main_page()  # Quay lại trang chính
    
    def delete_vocab_set_by_name(self, set_name):
        reply = QMessageBox.question(self, 'Xác nhận', 
                                    f'Bạn có chắc muốn xóa bộ từ vựng "{set_name}"?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if set_name in self.vocabulary_sets:
                del self.vocabulary_sets[set_name]
                self.data_manager.save_data(self.vocabulary_sets)
                self.update_vocab_sets_list()
                QMessageBox.information(self, 'Thành công', f'Đã xóa bộ từ vựng "{set_name}"')
    
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
                
                for set_name, vocab_items in imported_data.items():
                    if set_name in self.vocabulary_sets:
                        reply = QMessageBox.question(self, 'Xác nhận', 
                                                f'Bộ từ vựng "{set_name}" đã tồn tại. Bạn có muốn ghi đè không?',
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        
                        if reply == QMessageBox.No:
                            continue
                    
                    self.vocabulary_sets[set_name] = vocab_items
                
                self.data_manager.save_data(self.vocabulary_sets)
                self.update_vocab_sets_list()
                QMessageBox.information(self, 'Thành công', 'Đã nhập từ vựng thành công!')
            
            except Exception as e:
                QMessageBox.critical(self, 'Lỗi', f'Lỗi khi nhập file: {str(e)}')
    
    def closeEvent(self, event):
        self.data_manager.save_data(self.vocabulary_sets)
        event.accept()

    def load_categories(self):
        """Tải danh sách các danh mục từ dữ liệu"""
        categories = set()
        
        # Duyệt qua tất cả các bộ từ vựng
        for set_name, vocab_data in self.vocabulary_sets.items():
            # Kiểm tra nếu vocab_data là dict và có thuộc tính category
            if isinstance(vocab_data, dict) and 'category' in vocab_data:
                categories.add(vocab_data['category'])
        
        # Tạo thư mục categories nếu chưa tồn tại
        os.makedirs("data/categories", exist_ok=True)
        
        # Kiểm tra các thư mục danh mục đã tồn tại
        for item in os.listdir("data/categories"):
            if os.path.isdir(os.path.join("data/categories", item)):
                categories.add(item)
        
        return sorted(list(categories)) 
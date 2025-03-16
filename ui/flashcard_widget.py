import os
import tempfile
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QToolButton, QSizePolicy,
                            QSlider, QSpinBox, QFormLayout, QGroupBox,
                            QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
from gtts import gTTS
import pygame
import qtawesome as qta

class FlashcardWidget(QWidget):
    # Tín hiệu để thông báo khi muốn quay lại trang chính
    back_to_main = pyqtSignal()
    
    def __init__(self, vocab_items, parent=None, set_name="", category=""):
        super().__init__(parent)
        self.vocab_items = vocab_items
        self.current_index = 0
        self.show_meaning = False
        self.auto_play = False
        self.temp_dir = tempfile.mkdtemp()
        self.set_name = set_name  # Lưu tên bộ từ vựng
        self.category = category  # Lưu tên danh mục
        
        # Thời gian chờ mặc định (ms)
        self.wait_time_en = 3000  # 3 giây cho tiếng Anh
        self.wait_time_vi = 2000  # 2 giây cho tiếng Việt
        
        # Khởi tạo pygame để phát âm thanh
        pygame.mixer.init()
        
        # Khởi tạo timer cho chế độ tự động
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_play_step)
        
        # Thiết lập kích thước tối thiểu
        self.setMinimumSize(350, 300)
        
        self.initUI()
        self.update_card()
    
    def initUI(self):
        # Layout chính
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(3)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tạo scroll area để có thể cuộn khi cửa sổ nhỏ
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget chứa nội dung
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(3)
        content_layout.setContentsMargins(3, 3, 3, 3) 
        
        # Tiêu đề bộ từ vựng
        if self.set_name:
            title_text = self.set_name
            if self.category:
                title_text = f"{self.category} - {self.set_name}"
                
            self.title_label = QLabel(title_text)
            self.title_label.setAlignment(Qt.AlignCenter)
            self.title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            self.title_label.setStyleSheet("color: #2c3e50; margin-bottom: 3px;")
            content_layout.addWidget(self.title_label)
        
        # Thông tin thẻ
        self.info_label = QLabel(f"Thẻ 1/{len(self.vocab_items)}")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        content_layout.addWidget(self.info_label)
        
        # Thẻ ghi nhớ
        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.Box)
        self.card_frame.setLineWidth(1)
        self.card_frame.setMinimumHeight(120)
        self.card_frame.setCursor(Qt.PointingHandCursor)
        self.card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """)
        
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(5, 5, 5, 5)  # Giảm lề từ 8 xuống 5
        card_layout.setSpacing(3)  # Giảm khoảng cách từ 5 xuống 3
        
        # Từ vựng
        self.word_label = QLabel()
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.word_label.setStyleSheet("color: #2c3e50;")
        card_layout.addWidget(self.word_label)
        
        # Phiên âm (ẩn)
        self.pronunciation_label = QLabel()
        self.pronunciation_label.setAlignment(Qt.AlignCenter)
        self.pronunciation_label.setFont(QFont("Segoe UI", 12))
        self.pronunciation_label.setStyleSheet("color: #7f8c8d;")
        self.pronunciation_label.setVisible(False)
        card_layout.addWidget(self.pronunciation_label)
        
        # Đường kẻ phân cách
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #bdc3c7;")
        card_layout.addWidget(separator)
        
        # Nghĩa
        self.meaning_label = QLabel()
        self.meaning_label.setAlignment(Qt.AlignCenter)
        self.meaning_label.setFont(QFont("Segoe UI", 14))
        self.meaning_label.setWordWrap(True)
        self.meaning_label.setStyleSheet("color: #e74c3c;")
        card_layout.addWidget(self.meaning_label)
        
        content_layout.addWidget(self.card_frame)
        
        # Nhóm điều khiển thẻ
        card_control_group = QGroupBox("Điều khiển thẻ")
        card_control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        card_control_layout = QHBoxLayout(card_control_group)
        card_control_layout.setContentsMargins(2, 12, 2, 2)
        
        # Nút điều khiển
        # Nút trước
        self.prev_button = self.create_tool_button(qta.icon('fa5s.chevron-left', color='white'), "Trước")
        self.prev_button.clicked.connect(self.prev_card)
        card_control_layout.addWidget(self.prev_button)
        
        # Nút lật thẻ
        self.flip_button = self.create_tool_button(qta.icon('fa5s.sync', color='white'), "Lật thẻ")
        self.flip_button.clicked.connect(self.flip_card)
        card_control_layout.addWidget(self.flip_button)
        
        # Nút tiếp theo
        self.next_button = self.create_tool_button(qta.icon('fa5s.chevron-right', color='white'), "Tiếp theo")
        self.next_button.clicked.connect(self.next_card)
        card_control_layout.addWidget(self.next_button)
        
        content_layout.addWidget(card_control_group)
        
        # Nhóm điều khiển âm thanh
        audio_group = QGroupBox("Điều khiển âm thanh")
        audio_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        audio_layout = QHBoxLayout(audio_group)
        audio_layout.setContentsMargins(2, 12, 2, 2) 
        
        # Nút đọc từ
        self.speak_word_button = self.create_tool_button(qta.icon('fa5s.volume-up', color='white'), "Đọc từ")
        self.speak_word_button.clicked.connect(self.speak_word)
        audio_layout.addWidget(self.speak_word_button)
        
        # Nút đọc nghĩa
        self.speak_meaning_button = self.create_tool_button(qta.icon('fa5s.language', color='white'), "Đọc nghĩa")
        self.speak_meaning_button.clicked.connect(self.speak_meaning)
        audio_layout.addWidget(self.speak_meaning_button)
        
        # Nút tự động đọc
        self.auto_play_button = self.create_tool_button(qta.icon('fa5s.play', color='white'), "Tự động")
        self.auto_play_button.clicked.connect(self.toggle_auto_play)
        audio_layout.addWidget(self.auto_play_button)
        
        content_layout.addWidget(audio_group)
        
        # Nhóm cài đặt thời gian
        time_settings_group = QGroupBox("Cài đặt thời gian (giây)")
        time_settings_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        time_settings_layout = QFormLayout(time_settings_group)
        time_settings_layout.setContentsMargins(2, 12, 2, 2)  # Giảm lề từ (3, 15, 3, 3) xuống (2, 12, 2, 2)
        time_settings_layout.setVerticalSpacing(2)  # Giảm khoảng cách dọc từ 3 xuống 2
        
        # Thời gian chờ tiếng Anh
        en_time_layout = QHBoxLayout()
        
        self.en_time_spinbox = QSpinBox()
        self.en_time_spinbox.setRange(1, 10)
        self.en_time_spinbox.setValue(self.wait_time_en // 1000)  # Chuyển đổi từ ms sang giây
        self.en_time_spinbox.valueChanged.connect(self.update_en_wait_time)
        
        en_time_layout.addWidget(self.en_time_spinbox)
        time_settings_layout.addRow("Tiếng Anh:", en_time_layout)
        
        # Thời gian chờ tiếng Việt
        vi_time_layout = QHBoxLayout()
        
        self.vi_time_spinbox = QSpinBox()
        self.vi_time_spinbox.setRange(1, 10)
        self.vi_time_spinbox.setValue(self.wait_time_vi // 1000)  # Chuyển đổi từ ms sang giây
        self.vi_time_spinbox.valueChanged.connect(self.update_vi_wait_time)
        
        vi_time_layout.addWidget(self.vi_time_spinbox)
        time_settings_layout.addRow("Tiếng Việt:", vi_time_layout)
        
        content_layout.addWidget(time_settings_group)
        
        # Nút quay lại
        back_button = QPushButton("Quay lại")
        back_button.setIcon(qta.icon('fa5s.arrow-left', color='#3498db'))
        back_button.clicked.connect(self.back_to_main.emit)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                color: #2c3e50;
            }
            QPushButton:hover {
                background-color: #d6dbdf;
            }
            QPushButton:pressed {
                background-color: #bdc3c7;
            }
        """)
        content_layout.addWidget(back_button)
        
        # Thêm widget nội dung vào scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def create_tool_button(self, icon, tooltip):
        """Tạo nút công cụ với biểu tượng và tooltip"""
        button = QToolButton()
        button.setIcon(icon)
        button.setIconSize(QSize(16, 16))  # Giảm kích thước biểu tượng từ 20 xuống 16
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.setStyleSheet("""
            QToolButton {
                background-color: #3498db;
                border: none;
                border-radius: 4px;
                padding: 3px;  /* Giảm padding từ 5px xuống 3px */
            }
            QToolButton:hover {
                background-color: #2980b9;
            }
            QToolButton:pressed {
                background-color: #1f6aa5;
            }
        """)
        return button
    
    def update_card(self):
        """Cập nhật nội dung thẻ ghi nhớ"""
        if not self.vocab_items:
            return
        
        # Cập nhật thông tin thẻ
        self.info_label.setText(f"Thẻ {self.current_index + 1}/{len(self.vocab_items)}")
        
        # Lấy từ vựng hiện tại
        current_item = self.vocab_items[self.current_index]
        
        # Cập nhật từ vựng
        self.word_label.setText(current_item.get('word', ''))
        
        # Cập nhật nghĩa
        if self.show_meaning:
            self.meaning_label.setText(current_item.get('meaning', ''))
        else:
            self.meaning_label.setText("(Nhấp để xem nghĩa)")
    
    def flip_card(self):
        """Lật thẻ để hiển thị/ẩn nghĩa"""
        self.show_meaning = not self.show_meaning
        self.update_card()
    
    def next_card(self):
        """Chuyển đến thẻ tiếp theo"""
        if self.current_index < len(self.vocab_items) - 1:
            self.current_index += 1
            self.show_meaning = False  # Ẩn nghĩa khi chuyển sang thẻ mới
            self.update_card()
    
    def prev_card(self):
        """Quay lại thẻ trước"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_meaning = False  # Ẩn nghĩa khi chuyển sang thẻ mới
            self.update_card()
    
    def speak_word(self):
        """Đọc từ vựng bằng tiếng Anh"""
        if not self.vocab_items:
            return
        
        word_text = self.vocab_items[self.current_index].get('word', '')
        if not word_text:
            return
        
        try:
            # Tạo file âm thanh tiếng Anh
            tts = gTTS(text=word_text, lang='en', slow=False)
            word_file = os.path.join(self.temp_dir, f"word_{self.current_index}.mp3")
            tts.save(word_file)
            
            # Phát âm thanh
            pygame.mixer.music.load(word_file)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Lỗi khi đọc từ: {str(e)}")
    
    def speak_meaning(self):
        """Đọc nghĩa bằng tiếng Việt"""
        if not self.vocab_items:
            return
        
        meaning_text = self.vocab_items[self.current_index].get('meaning', '')
        if not meaning_text:
            return
        
        try:
            # Tạo file âm thanh tiếng Việt
            tts = gTTS(text=meaning_text, lang='vi', slow=False)
            meaning_file = os.path.join(self.temp_dir, f"meaning_{self.current_index}.mp3")
            tts.save(meaning_file)
            
            # Phát âm thanh
            pygame.mixer.music.load(meaning_file)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Lỗi khi đọc nghĩa: {str(e)}")
    
    def update_en_wait_time(self, value):
        """Cập nhật thời gian chờ tiếng Anh"""
        self.wait_time_en = value * 1000  # Chuyển đổi giây thành mili giây
    
    def update_vi_wait_time(self, value):
        """Cập nhật thời gian chờ tiếng Việt"""
        self.wait_time_vi = value * 1000  # Chuyển đổi giây thành mili giây
    
    def toggle_auto_play(self):
        """Bật/tắt chế độ tự động đọc"""
        self.auto_play = not self.auto_play
        
        if self.auto_play:
            self.auto_play_button.setIcon(qta.icon('fa5s.pause', color='white'))
            self.auto_play_button.setToolTip("Dừng tự động")
            self.auto_play_step_counter = 0
            self.show_meaning = False  # Bắt đầu với nghĩa ẩn
            self.update_card()
            self.start_auto_play()
        else:
            self.auto_play_button.setIcon(qta.icon('fa5s.play', color='white'))
            self.auto_play_button.setToolTip("Tự động đọc")
            self.timer.stop()
    
    def start_auto_play(self):
        """Bắt đầu quá trình tự động đọc"""
        self.auto_play_step_counter = 0
        self.timer.start(500)  # Bắt đầu với 0.5 giây
    
    def auto_play_step(self):
        """Xử lý các bước trong chế độ tự động đọc"""
        if not self.auto_play:
            return
            
        if self.auto_play_step_counter == 0:
            # Đọc từ tiếng Anh
            self.speak_word()
            self.timer.start(self.wait_time_en)  # Đợi theo thời gian đã cài đặt
            self.auto_play_step_counter = 1
        
        elif self.auto_play_step_counter == 1:
            # Hiển thị nghĩa và đọc nghĩa tiếng Việt
            self.show_meaning = True
            self.update_card()
            self.speak_meaning()
            self.timer.start(self.wait_time_vi)  # Đợi theo thời gian đã cài đặt
            self.auto_play_step_counter = 2
        
        elif self.auto_play_step_counter == 2:
            # Chuyển sang từ tiếp theo
            if self.current_index < len(self.vocab_items) - 1:
                self.current_index += 1
                self.show_meaning = False  # Ẩn nghĩa khi chuyển sang từ mới
                self.update_card()
                self.auto_play_step_counter = 0
                self.timer.start(500)  # Đợi 0.5 giây trước khi đọc từ mới
            else:
                # Đã đọc hết tất cả các từ
                self.toggle_auto_play()  # Tắt chế độ tự động
    
    def closeEvent(self, event):
        """Xử lý khi đóng widget"""
        # Dừng phát âm thanh nếu đang phát
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        
        # Xóa các file tạm
        for file in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, file))
            except:
                pass
        try:
            os.rmdir(self.temp_dir)
        except:
            pass
        
        event.accept() 
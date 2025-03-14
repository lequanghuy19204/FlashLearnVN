import os
import tempfile
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QToolButton, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from gtts import gTTS
import pygame
import qtawesome as qta  # Thêm thư viện qtawesome

class FlashcardWidget(QWidget):
    # Thêm tín hiệu để thông báo khi muốn quay lại trang chính
    back_to_main = pyqtSignal()
    
    def __init__(self, vocab_items, parent=None):
        super().__init__(parent)
        self.vocab_items = vocab_items
        self.current_index = 0
        self.show_meaning = False
        self.auto_play = False
        self.temp_dir = tempfile.mkdtemp()
        
        # Khởi tạo pygame để phát âm thanh
        pygame.mixer.init()
        
        # Khởi tạo timer cho chế độ tự động
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_play_step)
        
        self.initUI()
        self.update_card()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)  # Giảm khoảng cách
        layout.setContentsMargins(5, 5, 5, 5)  # Giảm margin
        
        # Thông tin thẻ
        self.info_label = QLabel(f"Thẻ 1/{len(self.vocab_items)}")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #7f8c8d; font-size: 8px;")
        layout.addWidget(self.info_label)
        
        # Thẻ ghi nhớ
        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.Box)
        self.card_frame.setLineWidth(1)
        self.card_frame.setMinimumSize(200, 120)  # Giảm kích thước thẻ
        self.card_frame.setMaximumHeight(120)  # Giới hạn chiều cao tối đa
        self.card_frame.setCursor(Qt.PointingHandCursor)
        self.card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #3498db;
                border-radius: 5px;
            }
        """)
        
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(5, 5, 5, 5)  # Giảm padding
        card_layout.setSpacing(3)  # Giảm khoảng cách
        
        # Từ vựng
        self.word_label = QLabel()
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setFont(QFont("Segoe UI", 12, QFont.Bold))  # Giảm kích thước font
        self.word_label.setStyleSheet("color: #2c3e50;")
        card_layout.addWidget(self.word_label)
        
        # Phiên âm (giữ lại nhưng ẩn đi)
        self.pronunciation_label = QLabel()
        self.pronunciation_label.setAlignment(Qt.AlignCenter)
        self.pronunciation_label.setFont(QFont("Segoe UI", 10))
        self.pronunciation_label.setStyleSheet("color: #7f8c8d;")
        self.pronunciation_label.setVisible(False)  # Ẩn label phiên âm
        card_layout.addWidget(self.pronunciation_label)
        
        # Nghĩa
        self.meaning_label = QLabel()
        self.meaning_label.setAlignment(Qt.AlignCenter)
        self.meaning_label.setFont(QFont("Segoe UI", 11))
        self.meaning_label.setWordWrap(True)
        self.meaning_label.setStyleSheet("color: #e74c3c;")
        card_layout.addWidget(self.meaning_label)
        
        # Thêm thẻ vào layout chính
        layout.addWidget(self.card_frame)
        
        # Nút điều khiển
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)  # Giảm khoảng cách
        
        # Nút trước - sử dụng icon từ qtawesome
        self.prev_button = self.create_tool_button(qta.icon('fa5s.chevron-left', color='white'), "Trước")
        self.prev_button.clicked.connect(self.prev_card)
        controls_layout.addWidget(self.prev_button)
        
        # Nút lật thẻ - sử dụng icon từ qtawesome
        self.flip_button = self.create_tool_button(qta.icon('fa5s.sync', color='white'), "Lật thẻ")
        self.flip_button.clicked.connect(self.flip_card)
        controls_layout.addWidget(self.flip_button)
        
        # Nút tiếp theo - sử dụng icon từ qtawesome
        self.next_button = self.create_tool_button(qta.icon('fa5s.chevron-right', color='white'), "Tiếp theo")
        self.next_button.clicked.connect(self.next_card)
        controls_layout.addWidget(self.next_button)
        
        layout.addLayout(controls_layout)
        
        # Nút phát âm
        audio_layout = QHBoxLayout()
        audio_layout.setSpacing(5)  # Giảm khoảng cách
        
        # Nút đọc từ - sử dụng icon từ qtawesome
        self.speak_word_button = self.create_tool_button(qta.icon('fa5s.volume-up', color='white'), "Đọc từ")
        self.speak_word_button.clicked.connect(self.speak_word)
        audio_layout.addWidget(self.speak_word_button)
        
        # Nút đọc nghĩa - sử dụng icon từ qtawesome
        self.speak_meaning_button = self.create_tool_button(qta.icon('fa5s.language', color='white'), "Đọc nghĩa")
        self.speak_meaning_button.clicked.connect(self.speak_meaning)
        audio_layout.addWidget(self.speak_meaning_button)
        
        # Nút tự động đọc - sử dụng icon từ qtawesome
        self.auto_play_button = self.create_tool_button(qta.icon('fa5s.play', color='white'), "Tự động")
        self.auto_play_button.clicked.connect(self.toggle_auto_play)
        audio_layout.addWidget(self.auto_play_button)
        
        layout.addLayout(audio_layout)
        
        # Nút quay lại
        back_layout = QHBoxLayout()
        
        self.back_button = QPushButton("Quay lại")
        self.back_button.setIcon(qta.icon('fa5s.arrow-left'))
        self.back_button.clicked.connect(self.go_back)
        back_layout.addWidget(self.back_button)
        
        layout.addLayout(back_layout)
        
        # Kết nối sự kiện click vào thẻ
        self.card_frame.mousePressEvent = self.flip_card_on_click
    
    def create_tool_button(self, icon, tooltip):
        """Tạo nút công cụ với icon"""
        button = QToolButton()
        button.setIcon(icon)
        button.setIconSize(QSize(16, 16))  # Giảm kích thước icon
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QToolButton {
                background-color: #3498db;
                border: 1px solid #2980b9;
                border-radius: 12px;
                padding: 3px;
            }
            QToolButton:hover {
                background-color: #2980b9;
            }
            QToolButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        button.setMinimumSize(QSize(30, 30))  # Giảm kích thước nút
        button.setMaximumSize(QSize(30, 30))  # Giới hạn kích thước tối đa
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return button
    
    def update_card(self):
        """Cập nhật nội dung thẻ ghi nhớ"""
        if not self.vocab_items:
            return
            
        self.info_label.setText(f"Thẻ {self.current_index + 1}/{len(self.vocab_items)}")
        
        item = self.vocab_items[self.current_index]
        self.word_label.setText(item['word'])
        
        # Ẩn label phiên âm vì không còn sử dụng
        self.pronunciation_label.setVisible(False)
        
        if self.show_meaning:
            self.meaning_label.setText(item['meaning'])
        else:
            self.meaning_label.setText("(Nhấp để xem nghĩa)")
    
    def flip_card(self):
        """Lật thẻ để hiển thị/ẩn nghĩa"""
        self.show_meaning = not self.show_meaning
        self.update_card()
    
    def flip_card_on_click(self, event):
        """Xử lý sự kiện click vào thẻ"""
        self.flip_card()
    
    def next_card(self):
        """Chuyển đến thẻ tiếp theo"""
        if self.current_index < len(self.vocab_items) - 1:
            self.current_index += 1
            self.show_meaning = False
            self.update_card()
    
    def prev_card(self):
        """Quay lại thẻ trước"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_meaning = False
            self.update_card()
    
    def go_back(self):
        """Quay lại trang chính"""
        # Dừng phát âm thanh nếu đang phát
        pygame.mixer.music.stop()
        
        # Dừng chế độ tự động nếu đang bật
        if self.auto_play:
            self.toggle_auto_play()
        
        # Phát tín hiệu để thông báo muốn quay lại trang chính
        self.back_to_main.emit()
    
    def speak_word(self):
        """Đọc từ tiếng Anh"""
        if not self.vocab_items:
            return
            
        item = self.vocab_items[self.current_index]
        word_text = item['word']
        
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
        """Đọc nghĩa tiếng Việt"""
        if not self.vocab_items:
            return
            
        item = self.vocab_items[self.current_index]
        meaning_text = item['meaning']
        
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
    
    def toggle_auto_play(self):
        """Bật/tắt chế độ tự động đọc"""
        self.auto_play = not self.auto_play
        
        if self.auto_play:
            self.auto_play_button.setIcon(qta.icon('fa5s.pause', color='white'))
            self.auto_play_button.setToolTip("Dừng tự động")
            self.auto_play_step_counter = 0
            self.show_meaning = True
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
            self.timer.start(5000)  # Đợi 5 giây trước khi đọc nghĩa
            self.auto_play_step_counter = 1
        
        elif self.auto_play_step_counter == 1:
            # Đọc nghĩa tiếng Việt
            self.speak_meaning()
            self.timer.start(2000)  # Đợi 2 giây trước khi chuyển sang từ tiếp theo
            self.auto_play_step_counter = 2
        
        elif self.auto_play_step_counter == 2:
            # Chuyển sang từ tiếp theo
            if self.current_index < len(self.vocab_items) - 1:
                self.current_index += 1
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
class VocabParser:
    def parse_vocab_text(self, vocab_text):
        """Phân tích văn bản từ vựng thành danh sách các từ"""
        vocab_items = []
        
        # Đảm bảo đầu vào là văn bản thuần túy
        if not isinstance(vocab_text, str):
            return vocab_items
        
        # Chuẩn hóa văn bản: thay thế nhiều dòng trống liên tiếp bằng một dấu phân cách đặc biệt
        normalized_text = vocab_text.replace('\r\n', '\n')  # Xử lý cả Windows line endings
        
        # Tách văn bản thành các dòng
        lines = normalized_text.split('\n')
        
        # Xử lý từng dòng
        i = 0
        while i < len(lines):
            current_line = lines[i].strip()
            
            # Bỏ qua dòng trống
            if not current_line:
                i += 1
                continue
            
            # Dòng hiện tại là từ vựng
            word = current_line
            meaning = ""
            
            # Kiểm tra dòng tiếp theo có phải là nghĩa không
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                
                # Nếu dòng tiếp theo không trống, đó là nghĩa
                if next_line:
                    meaning = next_line
                    i += 2  # Đã xử lý 2 dòng (từ và nghĩa)
                else:
                    # Dòng tiếp theo trống, tìm nghĩa ở dòng sau nữa
                    if i + 2 < len(lines) and lines[i + 2].strip():
                        meaning = lines[i + 2].strip()
                        i += 3  # Đã xử lý 3 dòng (từ, dòng trống, nghĩa)
                    else:
                        # Không tìm thấy nghĩa
                        i += 1  # Chỉ xử lý dòng từ vựng
            else:
                # Không còn dòng nào nữa
                i += 1
            
            # Thêm từ vào danh sách
            if word:  # Chỉ thêm nếu từ vựng không rỗng
                vocab_items.append({
                    'word': word,
                    'meaning': meaning
                })
        
        return vocab_items 
class VocabParser:
    def parse_vocab_text(self, vocab_text):
        """Phân tích văn bản từ vựng thành danh sách các từ"""
        vocab_items = []
        current_item = {}
        
        lines = vocab_text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:  # Bỏ qua dòng trống
                i += 1
                continue
                
            # Kiểm tra xem dòng có phải là từ mới không
            if "(" in line and "):" in line:
                # Lưu từ trước đó nếu có
                if current_item and 'word' in current_item and 'meaning' in current_item:
                    vocab_items.append(current_item)
                
                # Bắt đầu từ mới
                parts = line.split(':', 1)
                word_part = parts[0].strip()
                
                # Tách từ và loại từ
                word_type_parts = word_part.split('(')
                word = word_type_parts[0].strip()
                word_type = word_type_parts[1].split(')')[0].strip()
                
                current_item = {
                    'word': word,
                    'type': word_type
                }
                
                # Nếu có phần phiên âm và nghĩa trên dòng tiếp theo
                if i + 1 < len(lines) and lines[i + 1].strip():
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('/') and '/' in next_line[1:]:
                        # Tách phiên âm và nghĩa
                        parts = next_line.split('/', 2)
                        if len(parts) >= 3:
                            pronunciation = '/' + parts[1] + '/'
                            meaning = parts[2].strip()
                            current_item['pronunciation'] = pronunciation
                            current_item['meaning'] = meaning
                            i += 2  # Đã xử lý 2 dòng
                            continue
            
            # Nếu dòng hiện tại có thể là phiên âm và nghĩa
            elif line.startswith('/') and '/' in line[1:] and 'word' in current_item and 'type' in current_item:
                parts = line.split('/', 2)
                if len(parts) >= 3:
                    pronunciation = '/' + parts[1] + '/'
                    meaning = parts[2].strip()
                    current_item['pronunciation'] = pronunciation
                    current_item['meaning'] = meaning
            
            i += 1
        
        # Thêm từ cuối cùng nếu có
        if current_item and 'word' in current_item and 'meaning' in current_item:
            vocab_items.append(current_item)
            
        return vocab_items 
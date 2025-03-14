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
            
            # Trường hợp 1: Dòng có định dạng "word (type):"
            if "(" in line and "):" in line:
                # Lưu từ trước đó nếu có
                if current_item and 'word' in current_item:
                    # Đảm bảo các trường bắt buộc có giá trị mặc định nếu thiếu
                    if 'meaning' not in current_item:
                        current_item['meaning'] = ""
                    if 'pronunciation' not in current_item:
                        current_item['pronunciation'] = ""
                    if 'type' not in current_item:
                        current_item['type'] = ""
                    vocab_items.append(current_item)
                
                # Bắt đầu từ mới
                parts = line.split(':', 1)
                word_part = parts[0].strip()
                
                # Tách từ và loại từ
                word_type_parts = word_part.split('(')
                word = word_type_parts[0].strip()
                word_type = word_type_parts[1].split(')')[0].strip() if len(word_type_parts) > 1 else ""
                
                # Tạo item mới
                current_item = {
                    'word': word,
                    'type': word_type
                }
                
                # Kiểm tra dòng tiếp theo
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('/') and '/' in next_line[1:]:
                        # Dòng tiếp theo có phiên âm
                        parts = next_line.split('/', 2)
                        if len(parts) >= 3:
                            pronunciation = '/' + parts[1] + '/'
                            meaning = parts[2].strip()
                            current_item['pronunciation'] = pronunciation
                            current_item['meaning'] = meaning
                            i += 2  # Đã xử lý 2 dòng
                            continue
                    else:
                        # Dòng tiếp theo không có phiên âm, coi như là nghĩa
                        current_item['pronunciation'] = ""
                        current_item['meaning'] = next_line
                        i += 2  # Đã xử lý 2 dòng
                        continue
            
            # Trường hợp 2: Dòng có định dạng "word:" (không có loại từ)
            elif ":" in line and not ("(" in line and "):" in line):
                # Lưu từ trước đó nếu có
                if current_item and 'word' in current_item:
                    # Đảm bảo các trường bắt buộc có giá trị mặc định nếu thiếu
                    if 'meaning' not in current_item:
                        current_item['meaning'] = ""
                    if 'pronunciation' not in current_item:
                        current_item['pronunciation'] = ""
                    if 'type' not in current_item:
                        current_item['type'] = ""
                    vocab_items.append(current_item)
                
                # Bắt đầu từ mới
                parts = line.split(':', 1)
                word = parts[0].strip()
                
                # Tạo item mới không có loại từ
                current_item = {
                    'word': word,
                    'type': ""  # Loại từ trống
                }
                
                # Kiểm tra dòng tiếp theo
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('/') and '/' in next_line[1:]:
                        # Dòng tiếp theo có phiên âm
                        parts = next_line.split('/', 2)
                        if len(parts) >= 3:
                            pronunciation = '/' + parts[1] + '/'
                            meaning = parts[2].strip()
                            current_item['pronunciation'] = pronunciation
                            current_item['meaning'] = meaning
                            i += 2  # Đã xử lý 2 dòng
                            continue
                    else:
                        # Dòng tiếp theo không có phiên âm, coi như là nghĩa
                        current_item['pronunciation'] = ""
                        current_item['meaning'] = next_line
                        i += 2  # Đã xử lý 2 dòng
                        continue
            
            # Trường hợp 3: Dòng có phiên âm và nghĩa
            elif line.startswith('/') and '/' in line[1:] and 'word' in current_item:
                parts = line.split('/', 2)
                if len(parts) >= 3:
                    pronunciation = '/' + parts[1] + '/'
                    meaning = parts[2].strip()
                    current_item['pronunciation'] = pronunciation
                    current_item['meaning'] = meaning
            
            # Trường hợp 4: Dòng chỉ có nghĩa (không có phiên âm)
            elif 'word' in current_item and 'meaning' not in current_item:
                current_item['pronunciation'] = ""
                current_item['meaning'] = line
            
            i += 1
        
        # Thêm từ cuối cùng nếu có
        if current_item and 'word' in current_item:
            # Đảm bảo các trường bắt buộc có giá trị mặc định nếu thiếu
            if 'meaning' not in current_item:
                current_item['meaning'] = ""
            if 'pronunciation' not in current_item:
                current_item['pronunciation'] = ""
            if 'type' not in current_item:
                current_item['type'] = ""
            vocab_items.append(current_item)
            
        return vocab_items 
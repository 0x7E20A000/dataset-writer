from dataclasses import dataclass
import json
import re
import emoji
from typing import List, Dict

@dataclass
class NormalizationConfig:
    remove_emojis: bool = False
    normalize_punctuation: bool = True
    normalize_whitespace: bool = True
    max_consecutive_chars: int = 3

class TextNormalizer:
    def __init__(self, config: NormalizationConfig):
        self.config = config
        
    def normalize(self, text: str) -> str:
        if not text:
            return text
            
        if self.config.remove_emojis:
            text = emoji.replace_emoji(text, '')
        
        if self.config.normalize_punctuation:
            text = re.sub(r'[.]{2,}', '...', text)
            text = re.sub(r'[!?]{2,}', r'\1', text)
            text = re.sub(r'\s*([.,!?])\s*', r'\1 ', text)
            
        if self.config.normalize_whitespace:
            text = ' '.join(text.split())
            
        return text.strip()

class DataConverter:
    def __init__(self, system_message: str = "You are a helpful assistant."):
        self.system_message = system_message
        self.normalizer = TextNormalizer(NormalizationConfig())
        
    def save_to_jsonl(self, conversations: List[List[str]], output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            for conv in conversations:
                messages = [{"role": "system", "content": self.system_message}]
                
                for i, text in enumerate(conv):
                    role = "user" if i % 2 == 0 else "assistant"
                    messages.append({
                        "role": role,
                        "content": self.normalizer.normalize(text)
                    })
                    
                json.dump({"messages": messages}, f, ensure_ascii=False)
                f.write('\n')
from typing import Dict, List, Any, Union
import json
import emoji
import re
from dataclasses import dataclass

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
            # 문장 부호 정규화
            text = re.sub(r'[.]{2,}', '...', text)
            text = re.sub(r'[!?]{2,}', r'\1', text)
            text = re.sub(r'\s*([.,!?])\s*', r'\1 ', text)
            
        if self.config.normalize_whitespace:
            text = ' '.join(text.split())
            
        # 연속된 문자 정규화
        text = re.sub(r'(.)\1{' + str(self.config.max_consecutive_chars) + ',}', 
                     r'\1' * self.config.max_consecutive_chars, text)
            
        return text.strip()

class FineTuningDataConverter:
    def __init__(self, 
                 system_message: str = "You are a helpful assistant.",
                 normalization_config: NormalizationConfig = None,
                 max_turns: int = 4,
                 min_length: int = 10):
        self.system_message = system_message
        self.normalizer = TextNormalizer(normalization_config or NormalizationConfig())
        self.max_turns = max_turns
        self.min_length = min_length

    def contains_chinese(self, text: str) -> bool:
        """중국어 문자 포함 여부 확인"""
        return bool(re.search('[\u4e00-\u9fff]', text))

    def convert_conversation(self, conversation: List[str]) -> Union[Dict[str, List[Dict[str, str]]], None]:
        """대화를 OpenAI API 형식으로 변환"""
        # 중국어 포함 확인
        if any(self.contains_chinese(text) for text in conversation):
            return None
            
        messages = [
            {"role": "system", "content": self.system_message}
        ]
        
        # max_turns 제한 적용
        conversation = conversation[:self.max_turns * 2]  # user와 assistant 쌍을 고려
        
        for i, text in enumerate(conversation):
            normalized_text = self.normalizer.normalize(text)
            if not normalized_text:  # 빈 텍스트 건너뛰기
                continue
                
            # 최소 길이 확인
            if len(normalized_text) < self.min_length:
                continue
                
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({
                "role": role,
                "content": normalized_text
            })
            
        # 최소 1개의 대화 쌍이 있는지 확인 (system + user + assistant)
        return {"messages": messages} if len(messages) > 2 else None

    def save_to_jsonl(self, conversations: List[List[str]], output_file: str):
        """여러 대화를 JSONL 형식으로 저장"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for conv in conversations:
                result = self.convert_conversation(conv)
                if result:  # None이 아닌 경우만 저장
                    json.dump(result, f, ensure_ascii=False)
                    f.write('\n')

    def preview_conversation(self, conversation: List[str], colored: bool = True) -> None:
        """대화 미리보기"""
        try:
            from termcolor import colored as color_text
        except ImportError:
            colored = False
        
        print("\n=== Conversation Preview ===")
        print(f"System: {self.system_message}\n")
        
        for i, text in enumerate(conversation):
            role = "User" if i % 2 == 0 else "Assistant"
            normalized_text = self.normalizer.normalize(text)
            
            if colored:
                role_color = 'blue' if role == "User" else 'green'
                print(f"{color_text(role, role_color)}: {normalized_text}")
            else:
                print(f"{role}: {normalized_text}")
        print("===========================\n")
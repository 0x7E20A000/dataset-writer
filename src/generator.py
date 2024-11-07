from typing import List, Dict
import json
from .converter import FineTuningDataConverter, NormalizationConfig
import os
from datetime import datetime
from openai import OpenAI
from typing import Optional

class GPTsPromptGenerator:
    def __init__(self, 
                 domain: str,
                 style: str = "professional",
                 language: str = "Korean",
                 num_sets: int = 5,
                 api_key: Optional[str] = None):
        self.domain = domain
        self.style = style
        self.language = language
        self.num_sets = num_sets
        self.client = OpenAI(api_key=api_key)
        
    def generate_conversation(self, prompt: str) -> str:
        """OpenAI API를 사용하여 대화 생성"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # 또는 "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are an expert in creating training conversations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=5000,
                n=1,
                stop=None
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API 호출 실패: {str(e)}")
    
    def generate_conversation_prompt(self, topic: str, turns: int = 3) -> str:
        """대화 생성을 위한 프롬프트 생성"""
        prompt = f"""Create a natural conversation between a user and an assistant about {topic}.
The conversation should be:
- In {self.language}
- About {self.domain}
- In a {self.style} tone
- {turns} turns (question-answer pairs)
- Realistic and natural
- Include specific details and examples
- Show progression in the conversation

Format each turn as:
User: [user's question]
Assistant: [detailed, helpful response]

The assistant should:
1. Be knowledgeable about {self.domain}
2. Provide specific examples
3. Ask clarifying questions when needed
4. Give step-by-step explanations
5. Maintain a {self.style} tone throughout

Begin the conversation:"""
        return prompt
    
    def parse_gpt_response(self, response: str) -> List[str]:
        """GPT 응답을 대화 리스트로 변환"""
        lines = response.strip().split('\n')
        conversation = []
        
        for line in lines:
            if line.startswith(('User:', 'Assistant:')):
                content = line.split(':', 1)[1].strip()
                conversation.append(content)
                
        return conversation

# 컨버터 설정
config = NormalizationConfig(
    remove_emojis=False,
    normalize_punctuation=True,
    normalize_whitespace=True,
    max_consecutive_chars=3
)

# 컨버터 초기화
converter = FineTuningDataConverter(
    system_message="You are a helpful assistant.",
    normalization_config=config,
    max_turns=4,
    min_length=10
)

def generate_training_data(prompt: str, 
                         generator: GPTsPromptGenerator,
                         converter: FineTuningDataConverter,
                         prefix: str,
                         output_dir: str = "training_data",
                         callback=None):
    """
    여러 세트의 대화 데이터 생성 및 저장
    
    Args:
        prefix: 파일명 접두사 (예: "python_crawling")
        output_dir: 출력 디렉토리
        callback: 진행 상황을 보고하기 위한 콜백 함수
    """
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 타임스탬프
    timestamp = datetime.now().strftime("%Y%m%d")
    
    all_conversations = []
    
    # 여러 세트의 대화 생성
    for set_num in range(generator.num_sets):
        try:
            if callback:
                callback(f"Generating set {set_num + 1}/{generator.num_sets}...")
                
            # API를 통해 실제 대화 생성
            gpt_response = generator.generate_conversation(prompt)
            conversation = generator.parse_gpt_response(gpt_response)
            
            if not conversation:
                raise ValueError(f"Set {set_num + 1}: Invalid conversation format")
                
            all_conversations.append(conversation)
            
            # 각 세트별로 개별 파일 저장
            set_filename = f"{prefix}_set{set_num+1}_{timestamp}.jsonl"
            set_path = os.path.join(output_dir, set_filename)
            converter.save_to_jsonl([conversation], set_path)
            
            if callback:
                callback(f"Saved set {set_num + 1}")
                
        except Exception as e:
            if callback:
                callback(f"Error in set {set_num + 1}: {str(e)}")
            continue
    
    if all_conversations:
        # 모든 세트를 하나의 파일로도 저장
        combined_filename = f"{prefix}_combined_{timestamp}.jsonl"
        combined_path = os.path.join(output_dir, combined_filename)
        converter.save_to_jsonl(all_conversations, combined_path)
    
    return all_conversations

# 실행 예시
if __name__ == "__main__":
    # 생성기 초기화 (5세트 생성)
    generator = GPTsPromptGenerator(
        domain="Python Programming",
        style="friendly and educational",
        language="Korean",
        num_sets=5
    )

    # 주제별로 다른 프롬프트와 파일명으로 생성
    topics_and_prefixes = [
        ("웹 크롤링 기초", "python_crawling"),
        ("데이터 분석 기초", "data_analysis"),
        ("머신러닝 입문", "machine_learning")
    ]

    for topic, prefix in topics_and_prefixes:
        prompt = generator.generate_conversation_prompt(
            topic=topic,
            turns=3
        )
        
        conversations = generate_training_data(
            prompt=prompt,
            generator=generator,
            converter=converter,
            prefix=prefix,
            output_dir="training_data"
        )
        
        print(f"\n=== Generated {len(conversations)} sets for {topic} ===")
        # 첫 번째 세트 미리보기
        if conversations:
            converter.preview_conversation(conversations[0]) 
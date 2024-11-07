# main.py
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from config import (
    OPENAI_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    TOPICS,
    TOPIC_KEYWORDS,
    DEFAULT_CONFIG,
    SYSTEM_PROMPTS,
    OUTPUT_DIR
)
from converter import DataConverter  # JSONL 저장용 컨버터 클래스

def generate_conversations(topic: str, prefix: str, num_sets: int = DEFAULT_CONFIG["num_sets"]):
    load_dotenv()
    client = OpenAI(timeout=60.0)
    
    keywords = TOPIC_KEYWORDS.get(prefix, [])
    keywords_text = "\n".join(f"- {k}" for k in keywords)
    
    prompt = f"""주제 '{topic}'에 대한 자연스럽고 심도 있는 대화를 생성합니다. 

주요 키워드:
{keywords_text}

대화 형식:
- 총 3개의 질문-답변 쌍으로 구성합니다.
- 유저는 Assistant의 답변에 단순 공감이나 단조로운 피드백을 하지 않고, 구체적이고 실질적인 질문을 통해 대화를 확장시킵니다.
- 각 응답은 최소 500자 이상으로 작성해 주세요.

구성 예시:
1. User는 기본 개념에 대한 질문을 합니다.
2. Assistant는 개념 설명 후, 실무와의 관련성을 묻는 질문을 던집니다.
3. User는 단순 공감 없이, 실무 적용 사례나 추가 궁금증을 바탕으로 추가 질문을 이어갑니다.
4. Assistant는 이에 대해 깊이 있는 답변과 함께, 관련된 최신 동향을 언급하고, User의 의견을 묻는 질문으로 마무리합니다.

구체적인 형식은 다음과 같습니다:
User: [구체적인 질문]
Assistant: [상세한 답변과 유도 질문]"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["security_expert"]},
                {"role": "user", "content": prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            timeout=30
        )
        
        text = response.choices[0].message.content
        conversation = []
        
        for line in text.strip().split('\n'):
            if line.startswith(('User:', 'Assistant:')):
                content = line.split(':', 1)[1].strip()
                if content:
                    conversation.append(content)
        
        return [conversation] if conversation else []
            
    except Exception as e:
        print(f"Error generating conversation for {topic}: {str(e)}")
        return []
    
if __name__ == "__main__":
    converter = DataConverter(system_message=SYSTEM_PROMPTS["security_expert"])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for topic, prefix in TOPICS:
        conversations = generate_conversations(topic, prefix)  # prefix 전달
        if conversations:
            output_file = f"{OUTPUT_DIR}/{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jsonl"
            converter.save_to_jsonl(conversations, output_file)
            print(f"\nSaved {len(conversations)} conversations to {output_file}")
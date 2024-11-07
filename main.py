from openai import OpenAI
import os
from datetime import datetime
from converter import DataConverter
from dotenv import load_dotenv

def generate_conversations(topic: str, num_sets: int = 5, language: str = "Korean"):
    load_dotenv()
    client = OpenAI()
    
    prompt = f"""Create a natural conversation about {topic}.
The conversation should be:
- In {language}
- Realistic and natural
- Include specific details
- 3 turns (question-answer pairs)

Format as:
User: [question]
Assistant: [answer]"""

    conversations = []
    timestamp = datetime.now().strftime("%Y%m%d")
    
    print(f"\nGenerating {num_sets} conversations about '{topic}'...")
    
    for i in range(num_sets):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Create training conversations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            text = response.choices[0].message.content
            conversation = []
            
            for line in text.strip().split('\n'):
                if line.startswith(('User:', 'Assistant:')):
                    content = line.split(':', 1)[1].strip()
                    conversation.append(content)
            
            if conversation:
                conversations.append(conversation)
                print(f"Set {i+1}/{num_sets} completed")
                
        except Exception as e:
            print(f"Error in set {i+1}: {str(e)}")
            continue
    
    return conversations

if __name__ == "__main__":
    # 설정
    topics = [
        ("웹 크롤링 기초", "python_crawling"),
        ("데이터 분석 기초", "data_analysis"),
        ("머신러닝 입문", "machine_learning")
    ]
    
    converter = DataConverter()
    os.makedirs("training_data", exist_ok=True)
    
    # 각 주제별로 데이터 생성
    for topic, prefix in topics:
        conversations = generate_conversations(topic)
        if conversations:
            output_file = f"training_data/{prefix}_{datetime.now().strftime('%Y%m%d')}.jsonl"
            converter.save_to_jsonl(conversations, output_file)
            print(f"\nSaved {len(conversations)} conversations to {output_file}")

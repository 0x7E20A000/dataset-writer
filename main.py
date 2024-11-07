from openai import OpenAI
import os
from datetime import datetime
from converter import DataConverter
from dotenv import load_dotenv
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
def generate_conversations(
    topic: str, 
    prefix: str,  # prefix 파라미터 추가
    num_sets: int = DEFAULT_CONFIG["num_sets"],
    language: str = DEFAULT_CONFIG["language"]
):
    load_dotenv()
    client = OpenAI()
    
    # 주제별 키워드 가져오기
    keywords = TOPIC_KEYWORDS.get(prefix, [])
    keywords_text = "\n".join(f"- {k}" for k in keywords) if keywords else ""
    
    prompt = f"""Create a natural conversation about {topic}.
The conversation should be:
- In {language}
- About {DEFAULT_CONFIG['domain']}
- In a {DEFAULT_CONFIG['style']} tone
- Cover different aspects without repeating information
- Include specific technical details and examples
- Reference real-world applications

Topics to cover:
{keywords_text}

Format as:
User: [specific question about one aspect]
Assistant: [detailed answer with unique information]"""


    conversations = []
    
    print(f"\nGenerating {num_sets} conversations about '{topic}'...")
    
    for i in range(num_sets):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS["security_expert"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
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
    converter = DataConverter(system_message=SYSTEM_PROMPTS["security_expert"])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for topic, prefix in TOPICS:
        conversations = generate_conversations(topic, prefix)  # prefix 전달
        if conversations:
            output_file = f"{OUTPUT_DIR}/{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jsonl"
            converter.save_to_jsonl(conversations, output_file)
            print(f"\nSaved {len(conversations)} conversations to {output_file}")
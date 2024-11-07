import sys
import os
from dotenv import load_dotenv

# 상위 디렉토리의 src를 파이썬 패스에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QLineEdit, QCheckBox, QComboBox,
                           QTextEdit, QFileDialog, QSpinBox, QGroupBox)
from PyQt5.QtCore import Qt

# 임포트 경로 수정
from .converter import FineTuningDataConverter, NormalizationConfig
from .generator import GPTsPromptGenerator, generate_training_data

class FineTuningGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # .env 파일 로드
        load_dotenv()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Fine-Tuning Data Generator')
        self.setGeometry(100, 100, 800, 600)
        
        # 메인 위젯과 레이아웃
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # === 기본 설정 그룹 ===
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QVBoxLayout()
        
        # 시스템 메시지 설정
        system_layout = QHBoxLayout()
        self.system_label = QLabel('System Message:')
        self.system_input = QLineEdit()
        self.system_input.setText("You are a helpful assistant.")
        system_layout.addWidget(self.system_label)
        system_layout.addWidget(self.system_input)
        basic_layout.addLayout(system_layout)
        
        # 정규화 설정
        norm_layout = QHBoxLayout()
        self.remove_emojis_cb = QCheckBox('Remove Emojis')
        self.normalize_punct_cb = QCheckBox('Normalize Punctuation')
        self.normalize_punct_cb.setChecked(True)
        self.normalize_space_cb = QCheckBox('Normalize Whitespace')
        self.normalize_space_cb.setChecked(True)
        norm_layout.addWidget(self.remove_emojis_cb)
        norm_layout.addWidget(self.normalize_punct_cb)
        norm_layout.addWidget(self.normalize_space_cb)
        basic_layout.addLayout(norm_layout)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # === GPTs 설정 그룹 ===
        gpts_group = QGroupBox("GPTs Generation Settings")
        gpts_layout = QVBoxLayout()
        
        # 도메인 설정
        domain_layout = QHBoxLayout()
        self.domain_label = QLabel('Domain:')
        self.domain_input = QLineEdit()
        self.domain_input.setText("Python Programming")
        domain_layout.addWidget(self.domain_label)
        domain_layout.addWidget(self.domain_input)
        gpts_layout.addLayout(domain_layout)
        
        # 스타일과 언어 설정
        style_lang_layout = QHBoxLayout()
        self.style_label = QLabel('Style:')
        self.style_combo = QComboBox()
        self.style_combo.addItems(['professional', 'friendly and educational', 'casual'])
        self.language_label = QLabel('Language:')
        self.language_combo = QComboBox()
        self.language_combo.addItems(['Korean', 'English', 'Japanese'])
        style_lang_layout.addWidget(self.style_label)
        style_lang_layout.addWidget(self.style_combo)
        style_lang_layout.addWidget(self.language_label)
        style_lang_layout.addWidget(self.language_combo)
        gpts_layout.addLayout(style_lang_layout)
        
        # 세트 수와 턴 수 설정
        turns_layout = QHBoxLayout()
        self.num_sets_label = QLabel('Number of Sets:')
        self.num_sets_spin = QSpinBox()
        self.num_sets_spin.setRange(1, 20)
        self.num_sets_spin.setValue(5)
        self.max_turns_label = QLabel('Max Turns:')
        self.max_turns_spin = QSpinBox()
        self.max_turns_spin.setRange(1, 10)
        self.max_turns_spin.setValue(4)
        turns_layout.addWidget(self.num_sets_label)
        turns_layout.addWidget(self.num_sets_spin)
        turns_layout.addWidget(self.max_turns_label)
        turns_layout.addWidget(self.max_turns_spin)
        gpts_layout.addLayout(turns_layout)
        
        gpts_group.setLayout(gpts_layout)
        layout.addWidget(gpts_group)
        
        # === 주제 입력 영역 ===
        topics_group = QGroupBox("Topics")
        topics_layout = QVBoxLayout()
        
        self.topics_text = QTextEdit()
        self.topics_text.setPlaceholderText("Enter topics and prefixes (one per line)\nFormat: topic|prefix\nExample:\n웹 크롤링 기초|python_crawling\n데이터 분석 기초|data_analysis")
        topics_layout.addWidget(self.topics_text)
        
        topics_group.setLayout(topics_layout)
        layout.addWidget(topics_group)
        
        # API 키 설정 그룹 추가
        api_group = QGroupBox("OpenAI API Settings")
        api_layout = QVBoxLayout()
        
        # API 키 입력
        api_key_layout = QHBoxLayout()
        self.api_key_label = QLabel('API Key:')
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)  # 비밀번호 형식으로 표시
        api_key_layout.addWidget(self.api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        
        # API 키 입력 필드에 .env의 값 로드
        if api_key := os.getenv('OPENAI_API_KEY'):
            self.api_key_input.setText(api_key)
            
        api_layout.addLayout(api_key_layout)
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)  # 메인 레이아웃에 추가
        
        # === 실행 버튼과 상태 표시 ===
        button_layout = QHBoxLayout()
        self.generate_btn = QPushButton('Generate Training Data')
        self.generate_btn.clicked.connect(self.generate_training_data)
        button_layout.addWidget(self.generate_btn)
        
        self.status_label = QLabel('')
        button_layout.addWidget(self.status_label)
        
        layout.addLayout(button_layout)

    def generate_training_data(self):
        try:
            # API 키 확인
            api_key = self.api_key_input.text().strip()
            if not api_key:
                self.status_label.setText('Error: OpenAI API key is required')
                return
                
            # GPTs 생성기 초기화 시 API 키 전달
            generator = GPTsPromptGenerator(
                domain=self.domain_input.text(),
                style=self.style_combo.currentText(),
                language=self.language_combo.currentText(),
                num_sets=self.num_sets_spin.value(),
                api_key=api_key  # API 키 전달
            )
            
            # 설정 가져오기
            norm_config = NormalizationConfig(
                remove_emojis=self.remove_emojis_cb.isChecked(),
                normalize_punctuation=self.normalize_punct_cb.isChecked(),
                normalize_whitespace=self.normalize_space_cb.isChecked()
            )
            
            converter = FineTuningDataConverter(
                system_message=self.system_input.text(),
                normalization_config=norm_config,
                max_turns=self.max_turns_spin.value(),
                min_length=10
            )
            
            # 주제 파싱
            topics_text = self.topics_text.toPlainText()
            topics_and_prefixes = [
                tuple(line.strip().split('|'))
                for line in topics_text.split('\n')
                if line.strip() and '|' in line
            ]
            
            # 각 주제별로 데이터 생성
            for topic, prefix in topics_and_prefixes:
                prompt = generator.generate_conversation_prompt(
                    topic=topic,
                    turns=self.max_turns_spin.value()
                )
                
                conversations = generator.generate_conversation(
                    prompt=prompt,
                    generator=generator,
                    converter=converter,
                    prefix=prefix,
                    output_dir="training_data"
                )
                
                self.status_label.setText(f'Generated data for topic: {topic}')
                
            self.status_label.setText('All training data generated successfully!')
            
        except Exception as e:
            self.status_label.setText(f'Error: {str(e)}')

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    ex = FineTuningGUI()
    ex.show()
    sys.exit(app.exec_()) 
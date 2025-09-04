import openai
import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

# 페이지 설정
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 1rem;
}
.subtitle {
    text-align: center;
    color: #666;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}
.sidebar-header {
    color: #4facfe;
    font-weight: bold;
}
.warning-box {
    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
    border-left: 5px solid #ed8936;
    color: #f7fafc;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.error-box {
    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
    border-left: 5px solid #e53e3e;
    color: #f7fafc;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.info-box {
    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
    border-left: 5px solid #38b2ac;
    color: #f7fafc;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.stSelectbox > div > div {
    background-color: #2d3748 !important;
    border-radius: 10px;
    border: 1px solid #4a5568 !important;
}
.stSelectbox > div > div > div {
    color: #e2e8f0 !important;
}
.stTextInput > div > div > input {
    background-color: #2d3748 !important;
    color: #e2e8f0 !important;
    border-radius: 10px;
    border: 1px solid #4a5568 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4facfe !important;
    box-shadow: 0 0 0 0.2rem rgba(79, 172, 254, 0.15) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #a0aec0 !important;
}
/* 채팅 입력창 스타일링 */
.stChatInput > div > div > div > div > input {
    background-color: #2d3748 !important;
    color: #e2e8f0 !important;
    border: 1px solid #4a5568 !important;
    border-radius: 15px !important;
}
.stChatInput > div > div > div > div > input:focus {
    border-color: #4facfe !important;
    box-shadow: 0 0 0 0.2rem rgba(79, 172, 254, 0.15) !important;
}
.stChatInput > div > div > div > div > input::placeholder {
    color: #a0aec0 !important;
}

/* 복사 버튼 스타일 */
.copy-button {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 12px;
    cursor: pointer;
    margin-left: 10px;
    transition: all 0.3s ease;
    opacity: 0.7;
}

.copy-button:hover {
    opacity: 1;
    transform: scale(1.05);
}

.copy-button:active {
    transform: scale(0.95);
}

.message-container {
    position: relative;
}

.copy-success {
    background: linear-gradient(45deg, #56ab2f, #a8e6cf) !important;
}
</style>
""", unsafe_allow_html=True)

# 이미지를 base64로 인코딩하는 함수
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# 이미지 생성 함수 - DALL-E 3 API 연동
def generate_image(prompt, client):
    """
    DALL-E 3 API를 사용하여 이미지를 생성하는 함수
    
    Args:
        prompt (str): 이미지 생성을 위한 텍스트 프롬프트
        client (OpenAI): OpenAI 클라이언트 객체
    
    Returns:
        str or None: 생성된 이미지의 URL 또는 실패 시 None
    """
    try:
        # OpenAI의 images.generate API 호출
        response = client.images.generate(
            model="dall-e-3",           # DALL-E 3 모델 사용 (최신 버전)
            prompt=prompt,              # 사용자가 입력한 이미지 설명
            size="1024x1024",          # 이미지 크기 (1024x1024 픽셀)
            quality="standard",         # 이미지 품질 ("standard" 또는 "hd")
            n=1,                       # 생성할 이미지 개수 (DALL-E 3는 1개만 지원)
        )
        # 생성된 이미지의 URL 반환 (첫 번째 이미지)
        return response.data[0].url
    except Exception as e:
        # 오류 발생 시 Streamlit에 에러 메시지 표시하고 None 반환
        st.error(f"이미지 생성 중 오류가 발생했습니다: {str(e)}")
        return None

# 채팅 스타일별 시스템 메시지 함수
def get_system_message(style):
    base_message = "당신은 텍스트와 이미지를 모두 처리할 수 있는 AI 어시스턴트입니다. 이미지 분석, 이미지 생성 요청, 일반적인 질문 모두에 답변할 수 있습니다."
    
    if style == "친근하고 도움이 되는":
        return base_message + " 사용자의 질문에 따뜻하고 이해하기 쉽게 답변해주세요. 이모지를 적절히 사용하여 친근한 분위기를 만들어주세요."
    elif style == "전문적이고 정확한":
        return base_message + " 사실에 기반한 정확한 정보를 제공하고, 전문적인 톤으로 답변해주세요. 불확실한 정보는 명확히 표시해주세요."
    elif style == "창의적이고 재미있는":
        return base_message + " 유머와 창의성을 발휘하여 흥미롭고 재미있는 답변을 해주세요. 다양한 관점과 아이디어를 제시해주세요."
    else:  # 간결하고 명확한
        return base_message + " 핵심만 간단명료하게 답변해주세요. 불필요한 설명은 피하고 요점만 전달해주세요."

# 메인 제목과 구분선
st.markdown('<h1 class="main-header">🤖 AI Assistant Chatbot 💬</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">💡 무엇이든 물어보세요! Ask me anything! 🚀</p>', unsafe_allow_html=True)
st.markdown("---")

# 사이드바 스타일링
with st.sidebar:
    st.markdown('<h2 class="sidebar-header">⚙️ 설정 (Settings)</h2>', unsafe_allow_html=True)
    
    # API 키 입력
    st.markdown("---")
    openai_api_key = st.text_input(
        "🔑 OpenAI API Key", 
        type="password", 
        help="OpenAI API 키를 입력하세요.",
        placeholder="API 키를 입력하세요"
    )
    
    # 모델 선택
    st.markdown("---")
    st.markdown('<h3 class="sidebar-header">🧠 AI 모델 선택</h3>', unsafe_allow_html=True)
    model = st.selectbox(
        "사용할 AI 모델을 선택하세요:",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
        help="더 강력한 모델일수록 더 정확하지만 비용이 높습니다"
    )
    
    # 채팅 스타일
    st.markdown("---")
    st.markdown('<h3 class="sidebar-header">🎭 채팅 스타일</h3>', unsafe_allow_html=True)
    chat_style = st.selectbox(
        "AI의 응답 스타일을 선택하세요:",
        ["친근하고 도움이 되는", "전문적이고 정확한", "창의적이고 재미있는", "간결하고 명확한"],
        index=0,
        help="AI가 어떤 톤으로 응답할지 선택하세요"
    )
    
    # 이미지 업로드
    st.markdown("---")
    st.markdown('<h3 class="sidebar-header">🖼️ 이미지 업로드</h3>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "이미지를 업로드하세요",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
        help="업로드한 이미지를 AI가 분석해드립니다"
    )
    
    if uploaded_file is not None:
        # 이미지 미리보기
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", width=200)
        
        if st.button("📤 이미지 전송", use_container_width=True):
            # 이미지를 base64로 인코딩
            encoded_image = encode_image(image)
            
            # 메시지에 이미지 추가
            image_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "이 이미지를 분석해주세요."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image}"
                        }
                    }
                ]
            }
            st.session_state.messages.append(image_message)
            st.success("이미지가 전송되었습니다!")
            st.rerun()
    
    # 채팅 옵션
    st.markdown("---")
    st.markdown('<h3 class="sidebar-header">💬 채팅 옵션</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 초기화", help="대화 기록을 모두 삭제합니다"):
            st.session_state.messages = [
                {"role": "system", 
                "content": get_system_message(chat_style)}
            ]
            st.success("대화 기록이 초기화되었습니다!")
            st.rerun()
    
    with col2:
        if st.button("ℹ️ 도움말"):
            st.session_state.show_help_modal = True

# 도움말 모달
if "show_help_modal" in st.session_state and st.session_state.show_help_modal:
    # 모달 배경 클릭으로 닫기
    if st.button("❌", key="close_modal_bg", help="모달 닫기"):
        st.session_state.show_help_modal = False
        st.rerun()
    
    # 모달 내용을 expander로 구현
    with st.expander("🤖 AI 어시스턴트 사용법", expanded=True):
        st.markdown("""
        ### 🚀 시작하기:
        1. 🔑 **OpenAI API 키**를 입력하세요
        2. 🧠 **AI 모델**을 선택하세요  
        3. 🎭 **채팅 스타일**을 선택하세요
        4. 💬 **무엇이든 질문**해보세요!
        
        ### 💡 할 수 있는 일들:
        - 📚 학습 및 교육 도움
        - 💻 프로그래밍 및 코딩 지원
        - 📝 글쓰기 및 번역
        - 🧮 수학 및 계산 문제 해결
        - 🎨 창작 및 아이디어 제안
        - 📊 데이터 분석 및 해석
        - 🔍 정보 검색 및 요약
        - 🖼️ 이미지 분석 및 설명
        - 🎭 이미지 생성 (DALL-E)
        
        ### ⚡ 팁:
        - 구체적으로 질문할수록 더 정확한 답변을 받을 수 있어요
        - 단계별로 설명이 필요하면 "단계별로 설명해줘"라고 요청하세요
        - 예시가 필요하면 "예시를 들어줘"라고 말씀하세요
        - 이미지 생성: "고양이 그림 그려줘" 또는 "/image 고양이"
        - 이미지 업로드: 사이드바에서 이미지 파일을 업로드하세요
        """)
        
        # 닫기 버튼
        if st.button("✅ 확인", key="close_modal_btn", use_container_width=True):
            st.session_state.show_help_modal = False
            st.rerun()


if not openai_api_key:
    st.markdown("""
    <div class="warning-box">
        <h4>🔑 API 키가 필요합니다</h4>
        <p>AI 어시스턴트를 사용하려면 OpenAI API 키를 입력해주세요.</p>
        <p><small>💡 <strong>도움말:</strong> OpenAI 웹사이트에서 API 키를 발급받을 수 있습니다.</small></p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# 잘못된 형태 키입력 에러 추가
if not openai_api_key.startswith("sk-"):
    st.markdown("""
    <div class="error-box">
        <h4>❌ 잘못된 API 키 형식</h4>
        <p>OpenAI API 키는 'sk-'로 시작해야 합니다.</p>
        <p><small>💡 <strong>형식:</strong> 올바른 OpenAI API 키를 입력해주세요</small></p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# API 키 검증
try:
    client = OpenAI(api_key=openai_api_key)
    # 간단한 테스트 호출로 키 유효성 검증
    test_response = client.models.list()
except openai.AuthenticationError:
    st.markdown("""
    <div class="error-box">
        <h4>🚫 인증 실패</h4>
        <p>입력하신 API 키가 유효하지 않습니다.</p>
        <p><small>💡 <strong>확인사항:</strong> API 키가 올바르게 입력되었는지, 계정에 충분한 크레딧이 있는지 확인해주세요.</small></p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
except Exception as e:
    st.markdown(f"""
    <div class="error-box">
        <h4>⚠️ 연결 오류</h4>
        <p>OpenAI API 연결 중 문제가 발생했습니다.</p>
        <p><small>🔧 <strong>오류 내용:</strong> {str(e)}</small></p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# 성공 메시지
st.markdown("""
<div class="info-box">
    <p>✅ <strong>연결 성공!</strong> AI 어시스턴트가 준비되었습니다. 무엇이든 물어보세요! 🎉</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", 
        "content": get_system_message("친근하고 도움이 되는")}
    ]

# 스타일 변경 시 시스템 메시지 업데이트
if st.session_state.messages[0]["content"] != get_system_message(chat_style):
    st.session_state.messages[0]["content"] = get_system_message(chat_style)

# 대화내용 표시
for idx, message in enumerate(st.session_state.messages):
    if message['role'] != "system":
        with st.chat_message(message["role"]):
            # 이미지가 포함된 메시지 처리
            if isinstance(message["content"], list):
                for content in message["content"]:
                    if content["type"] == "text":
                        st.markdown(content["text"])
                    elif content["type"] == "image_url":
                        st.image(content["image_url"]["url"], caption="업로드된 이미지")
            else:
                st.markdown(message["content"])
            
            # 복사 버튼과 영역을 메시지 하단에 표시
            copy_key = f"copy_{message['role']}_{idx}"
            
            # 메시지 내용 추출
            if isinstance(message["content"], list):
                text_content = ""
                for content in message["content"]:
                    if content["type"] == "text":
                        text_content += content["text"]
            else:
                text_content = message["content"]
            
            # 복사 버튼
            if st.button("📋 복사", key=copy_key, help="메시지 복사"):
                st.session_state[f"show_copy_{copy_key}"] = True
                st.rerun()
            
            # 복사 영역 표시
            if st.session_state.get(f"show_copy_{copy_key}", False):
                st.text_area(
                    "복사할 텍스트:",
                    value=text_content,
                    height=100,
                    key=f"copy_area_{copy_key}",
                    help="텍스트를 선택하고 Ctrl+C (또는 Cmd+C)로 복사하세요"
                )
                if st.button("❌ 닫기", key=f"close_{copy_key}"):
                    st.session_state[f"show_copy_{copy_key}"] = False
                    st.rerun()

# 채팅 입력 필드
# 스타일별 플레이스홀더 텍스트
placeholder_text = {
    "친근하고 도움이 되는": "안녕하세요! 무엇을 도와드릴까요? 😊",
    "전문적이고 정확한": "질문을 입력해주세요. 정확한 답변을 드리겠습니다.",
    "창의적이고 재미있는": "재미있는 질문이나 아이디어를 들려주세요! 🎨",
    "간결하고 명확한": "질문을 입력하세요."
}

if prompt := st.chat_input(placeholder_text[chat_style]):
    # 이미지 생성 요청 키워드 감지
    # 한국어와 영어 키워드를 모두 체크하여 이미지 생성 요청인지 판단
    is_image_request = any(keyword in prompt.lower() for keyword in [
        "그림", "이미지", "그려", "생성", "/image", "draw", "create image", "make image"
    ])
    
    if is_image_request:
        # 이미지 생성 요청 처리 분기
        with st.chat_message("user"):
            st.markdown(prompt)  # 사용자 입력 메시지 표시
        
        with st.chat_message("assistant"):
            # 이미지 생성 중 로딩 스피너 표시
            with st.spinner("이미지를 생성하고 있습니다... 🎨"):
                # "/image" 접두사가 있다면 제거하여 순수한 프롬프트만 추출
                clean_prompt = prompt.replace("/image", "").strip()
                
                # DALL-E 3 API 호출하여 이미지 생성
                image_url = generate_image(clean_prompt, client)
                
                if image_url:
                    # 생성 성공 시: 이미지 표시 + 성공 메시지
                    st.image(image_url, caption=f"생성된 이미지: {clean_prompt}")
                    st.markdown(f"✨ **{clean_prompt}**에 대한 이미지를 생성했습니다!")
                else:
                    # 생성 실패 시: 에러 메시지 표시
                    st.error("이미지 생성에 실패했습니다. 다시 시도해주세요.")
        
        # 대화 기록에 사용자 메시지와 AI 응답 저장
        st.session_state.messages.append({"role": "user", "content": prompt})
        if image_url:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"이미지를 생성했습니다: {clean_prompt}\n이미지 URL: {image_url}"
            })
    else:
        # 일반 텍스트 대화 처리
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI API 스트리밍 호출
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # 스트리밍 응답을 채팅으로 표시하고 세션에 저장
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

import openai
import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="Travel Chatbot",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
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
    color: #4a90e2;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# 메인 제목
st.markdown('<h1 class="main-header">✈️ Travel Assistant Chatbot 🗺️</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">🌍 전 세계 여행 정보를 한 곳에서! Ask me anything about travel! 🧳</p>', unsafe_allow_html=True)

st.sidebar.markdown('<h2 class="sidebar-header">⚙️ 설정 (Settings)</h2>', unsafe_allow_html=True)
openai_api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password", help="OpenAI API 키를 입력하세요")

# 언어 선택
st.sidebar.markdown('<h3 class="sidebar-header">🌐 언어 선택 (Language)</h3>', unsafe_allow_html=True)
language = st.sidebar.selectbox(
    "응답 언어를 선택하세요:",
    ["한국어 (Korean)", "English", "한국어 + English (Both)"],
    index=2
)


if not openai_api_key:
    st.warning("OpenAI API Key가 입력되지 않았습니다.")
    st.stop()

# 잘못된 형태 키입력 에러 추가
if not openai_api_key.startswith("sk-"):
    st.warning("OpenAI API Key가 잘못된 형태입니다.")
    st.stop()

# 잘못된 키 에러 추가
try:
    client = OpenAI(api_key=openai_api_key)
except openai.OpenAIError as e:
    st.error(f"OpenAI API 호출 중 오류 발생: {e}")
    st.stop()

# 언어별 시스템 메시지 함수
def get_system_message(language):
    if language == "English":
        return "You are a helpful travel chatbot. Answer only travel-related questions in English. If asked about non-travel topics, politely decline. Provide information about destinations, preparations, culture, food, and other travel topics."
    elif language == "한국어 (Korean)":
        return "당신은 여행에 관한 질문에 답하는 챗봇입니다. 한국어로만 답변해주세요. 여행 외의 질문이 와도 답변하지 않습니다. 여행지 추천, 준비물, 문화, 음식 등 다양한 주제에 대해 친절하게 안내하는 챗봇입니다."
    else:  # Both languages
        return "당신은 여행에 관한 질문에 답하는 챗봇입니다. 한국어와 영어로 답변해주세요. You are a travel chatbot that answers in both Korean and English. 여행 외의 질문이 와도 답변하지 않습니다. Only answer travel-related questions. 여행지 추천, 준비물, 문화, 음식 등에 대해 친절하게 안내해주세요."

st.sidebar.markdown('<h3 class="sidebar-header">💬 채팅 옵션</h3>', unsafe_allow_html=True)
if st.sidebar.button("🗑️ 대화 기록 삭제"):
    st.session_state.messages = [
        {"role": "system", 
        "content": get_system_message(language)}
    ]
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", 
        "content": get_system_message("한국어 + English (Both)")}
    ]

# 언어 변경 시 시스템 메시지 업데이트
if st.session_state.messages[0]["content"] != get_system_message(language):
    st.session_state.messages[0]["content"] = get_system_message(language)

# 대화내용 표시
for message in st.session_state.messages:
    if message['role'] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 채팅 입력 필드
# 언어별 플레이스홀더 텍스트
placeholder_text = {
    "한국어 (Korean)": "여행에 대해 궁금한 것을 물어보세요! 🌟",
    "English": "Ask me anything about travel! 🌟",
    "한국어 + English (Both)": "여행에 대해 물어보세요! Ask me about travel! 🌟"
}

if prompt := st.chat_input(placeholder_text[language]):
    
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # OpenAI API 스트리밍 호출
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
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

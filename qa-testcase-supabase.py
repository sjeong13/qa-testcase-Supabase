# test_app.py
import streamlit as st

st.title("🔐 환경 변수 확인")

try:
    supabase_url = st.secrets.get("SUPABASE_URL", "❌ 없음")
    supabase_key = st.secrets.get("SUPABASE_KEY", "❌ 없음")
    google_key = st.secrets.get("GOOGLE_API_KEY", "❌ 없음")
    app_password = st.secrets.get("APP_PASSWORD", "❌ 없음")
    
    st.success("✅ secrets.toml 파일을 성공적으로 읽었습니다!")
    
    st.write("**SUPABASE_URL:**", supabase_url[:30] + "..." if len(supabase_url) > 30 else supabase_url)
    st.write("**SUPABASE_KEY:**", supabase_key[:30] + "..." if len(supabase_key) > 30 else supabase_key)
    st.write("**GOOGLE_API_KEY:**", google_key[:30] + "..." if len(google_key) > 30 else google_key)
    st.write("**APP_PASSWORD:**", "✅ 설정됨" if app_password != "❌ 없음" else "❌ 없음")
    
except Exception as e:
    st.error(f"❌ 에러: {e}")
    st.info("💡 .streamlit/secrets.toml 파일이 올바르게 생성되었는지 확인하세요.")

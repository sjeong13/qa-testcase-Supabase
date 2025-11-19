import streamlit as st
from supabase import create_client

# Supabase 연결
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("Supabase 연결 테스트")

# 1. 테이블 존재 확인
if st.button("테이블 확인"):
    try:
        result = supabase.table('test_cases').select('*').limit(1).execute()
        st.success("✅ test_cases 테이블 연결 성공!")
        st.write(f"데이터 개수: {len(result.data)}개")
    except Exception as e:
        st.error(f"❌ 연결 실패: {str(e)}")

# 2. 테스트 데이터 삽입
if st.button("테스트 데이터 추가"):
    try:
        result = supabase.table('test_cases').insert({
            "category": "테스트",
            "name": "연결 테스트",
            "description": "Supabase 연결 확인용",
            "data": {"test": True}
        }).execute()
        st.success("✅ 데이터 추가 성공!")
        st.json(result.data)
    except Exception as e:
        st.error(f"❌ 추가 실패: {str(e)}")

# 3. 데이터 조회
if st.button("데이터 조회"):
    try:
        result = supabase.table('test_cases').select('*').execute()
        st.success(f"✅ {len(result.data)}개 조회!")
        st.json(result.data)
    except Exception as e:
        st.error(f"❌ 조회 실패: {str(e)}")

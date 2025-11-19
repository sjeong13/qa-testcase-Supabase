import streamlit as st
from supabase import create_client
import google.generativeai as genai
import os

# Supabase 연결
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Gemini 연결
api_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

st.title("🧪 Supabase + 벡터 검색 테스트")

# ============================================
# 1. 테이블 연결 테스트
# ============================================
st.header("1️⃣ 테이블 연결 테스트")
if st.button("테이블 확인"):
    try:
        result = supabase.table('test_cases').select('*').limit(1).execute()
        st.success("✅ test_cases 테이블 연결 성공!")
        st.write(f"데이터 개수: {len(result.data)}개")
    except Exception as e:
        st.error(f"❌ 연결 실패: {str(e)}")

st.markdown("---")

# ============================================
# 2. 임베딩 생성 테스트
# ============================================
st.header("2️⃣ 임베딩 생성 테스트")

test_text = st.text_area(
    "테스트 텍스트 입력",
    value="쿠폰 지정 발행 테스트 케이스",
    height=100
)

if st.button("임베딩 생성"):
    try:
        with st.spinner("임베딩 생성 중..."):
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=test_text,
                task_type="retrieval_document"
            )
            embedding = result['embedding']

            st.success(f"✅ 임베딩 생성 성공!")
            st.write(f"**차원:** {len(embedding)}차원")
            st.write(f"**처음 10개 값:** {embedding[:10]}")

            # 세션에 저장
            st.session_state.test_embedding = embedding

    except Exception as e:
        st.error(f"❌ 임베딩 생성 실패: {str(e)}")

st.markdown("---")

# ============================================
# 3. 임베딩과 함께 데이터 저장
# ============================================
st.header("3️⃣ 임베딩 저장 테스트")

col1, col2 = st.columns(2)
with col1:
    save_category = st.text_input("카테고리", value="쿠폰")
with col2:
    save_name = st.text_input("이름", value="쿠폰 발행 테스트")

save_description = st.text_area(
    "설명",
    value="BO에서 쿠폰을 생성하고 특정 회원에게 지정 발행하는 테스트",
    height=100
)

if st.button("임베딩과 함께 저장"):
    try:
        # 1. 임베딩 생성
        search_text = f"{save_category} {save_name} {save_description}"

        with st.spinner("임베딩 생성 중..."):
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=search_text,
                task_type="retrieval_document"
            )
            embedding = result['embedding']

        # 2. Supabase에 저장
        with st.spinner("Supabase에 저장 중..."):
            insert_result = supabase.table('test_cases').insert({
                "category": save_category,
                "name": save_name,
                "description": save_description,
                "data": {
                    "category": save_category,
                    "name": save_name,
                    "description": save_description
                },
                "embedding": embedding
            }).execute()

        st.success("✅ 저장 완료!")
        st.json(insert_result.data)

    except Exception as e:
        st.error(f"❌ 저장 실패: {str(e)}")

st.markdown("---")

# ============================================
# 4. 저장된 데이터 조회
# ============================================
st.header("4️⃣ 저장된 데이터 조회")

if st.button("전체 데이터 조회"):
    try:
        result = supabase.table('test_cases').select('id, category, name, description, created_at').execute()
        st.success(f"✅ {len(result.data)}개 조회!")

        import pandas as pd
        if result.data:
            df = pd.DataFrame(result.data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    except Exception as e:
        st.error(f"❌ 조회 실패: {str(e)}")

st.markdown("---")

# ============================================
# 5. 벡터 검색 테스트
# ============================================
st.header("5️⃣ 벡터 유사도 검색 테스트")

search_query = st.text_input(
    "검색어 입력",
    value="할인 코드 생성",
    placeholder="예: 쿠폰 사용, 프로모션 등록"
)

if st.button("벡터 검색 실행"):
    try:
        # 1. 검색어 임베딩
        with st.spinner("검색어 임베딩 생성 중..."):
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=search_query,
                task_type="retrieval_query"  # 검색용
            )
            query_embedding = result['embedding']

        # 2. 벡터 검색 (RPC 함수 호출)
        with st.spinner("유사도 검색 중..."):
            search_result = supabase.rpc(
                'match_test_cases',
                {
                    'query_embedding': query_embedding,
                    'match_count': 10,
                    'similarity_threshold': 0.3
                }
            ).execute()

        # 3. 결과 표시
        if search_result.data:
            st.success(f"✅ {len(search_result.data)}개 발견!")

            for idx, item in enumerate(search_result.data, 1):
                similarity = item['similarity']

                # 유사도에 따른 색상
                if similarity > 0.8:
                    color = "🟢"
                elif similarity > 0.6:
                    color = "🟡"
                else:
                    color = "🟠"

                with st.expander(f"{color} {idx}. {item['name']} (유사도: {similarity:.2%})"):
                    st.write(f"**카테고리:** {item['category']}")
                    st.write(f"**설명:** {item['description']}")
                    st.write(f"**유사도:** {similarity:.4f}")
        else:
            st.warning("검색 결과가 없습니다.")

    except Exception as e:
        st.error(f"❌ 검색 실패: {str(e)}")
        st.write("상세 에러:", str(e))

st.markdown("---")

# ============================================
# 6. 데이터 삭제 (테스트용)
# ============================================
st.header("6️⃣ 테스트 데이터 삭제")

if st.button("⚠️ 모든 데이터 삭제", type="secondary"):
    if st.checkbox("정말 삭제하시겠습니까?"):
        try:
            # 전체 데이터 조회 후 삭제
            result = supabase.table('test_cases').select('id').execute()
            for item in result.data:
                supabase.table('test_cases').delete().eq('id', item['id']).execute()

            st.success(f"✅ {len(result.data)}개 삭제 완료!")
        except Exception as e:
            st.error(f"❌ 삭제 실패: {str(e)}")

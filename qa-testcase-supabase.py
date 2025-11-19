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


st.markdown("---")

# ============================================
# 7. 개별 저장 테스트
# ============================================
st.header("7️⃣ 개별 저장 테스트")

st.info("💡 그룹 데이터를 개별 케이스로 쪼개서 저장하는 테스트")

# supabase_helpers import
try:
    from supabase_helpers import save_test_case_to_supabase, search_similar_test_cases
    st.success("✅ supabase_helpers 로드 성공")
except ImportError as e:
    st.error(f"❌ supabase_helpers.py 파일이 필요합니다: {str(e)}")
    st.stop()

# 테스트용 그룹 데이터
test_group = {
    "group_id": "test_group_001",
    "input_type": "table_group",
    "name": "테스트 그룹 (3개)",
    "table_data": [
        {
            "NO": "1",
            "CATEGORY": "쿠폰",
            "DEPTH 1": "쿠폰 발행",
            "DEPTH 2": "지정 발행",
            "DEPTH 3": "",
            "PRE-CONDITION": "쿠폰 생성 완료",
            "STEP": "BO에서 쿠폰 지정 발행",
            "EXPECT RESULT": "회원에게 쿠폰 발급됨"
        },
        {
            "NO": "2",
            "CATEGORY": "쿠폰",
            "DEPTH 1": "쿠폰 사용",
            "DEPTH 2": "결제 시 사용",
            "DEPTH 3": "",
            "PRE-CONDITION": "쿠폰 발급 완료",
            "STEP": "FO에서 쿠폰 사용",
            "EXPECT RESULT": "할인 적용됨"
        },
        {
            "NO": "3",
            "CATEGORY": "쿠폰",
            "DEPTH 1": "쿠폰 삭제",
            "DEPTH 2": "관리자 삭제",
            "DEPTH 3": "",
            "PRE-CONDITION": "쿠폰 존재",
            "STEP": "BO에서 쿠폰 삭제",
            "EXPECT RESULT": "쿠폰 삭제됨"
        }
    ]
}

col1, col2 = st.columns(2)

with col1:
    if st.button("🧪 그룹 저장 테스트 (3개 → 3 rows)", use_container_width=True):
        with st.spinner("개별 케이스로 쪼개서 저장 중..."):
            count = save_test_case_to_supabase(test_group)
        
        if count > 0:
            st.success(f"✅ {count}개 개별 저장 완료!")
            st.info("👉 '4️⃣ 저장된 데이터 조회'에서 확인하세요")
        else:
            st.error("❌ 저장 실패")

with col2:
    if st.button("🔍 개별 검색 테스트", use_container_width=True):
        with st.spinner("'쿠폰 사용'으로 검색 중..."):
            results = search_similar_test_cases("쿠폰 사용", limit=10)
        
        if results:
            st.success(f"✅ {len(results)}개 발견!")
            for r in results:
                similarity = r.get('similarity', 0)
                st.write(f"- **{r.get('name')}** (유사도: {similarity:.2%})")
        else:
            st.warning("검색 결과 없음")

st.markdown("---")

# ============================================
# 8. Supabase 데이터 확인
# ============================================
st.header("8️⃣ Supabase 직접 확인")

if st.button("📊 Supabase 전체 데이터 (상세)"):
    try:
        result = supabase.table('test_cases').select('*').execute()
        
        st.write(f"**총 {len(result.data)}개**")
        
        import pandas as pd
        if result.data:
            # 주요 컬럼만 표시
            display_data = []
            for row in result.data:
                display_data.append({
                    'id': row['id'],
                    'category': row['category'],
                    'name': row['name'],
                    'group_id': row['data'].get('group_id', '-'),
                    'created_at': row['created_at']
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
            
            # group_id로 그룹핑
            groups = {}
            for row in result.data:
                gid = row['data'].get('group_id')
                if gid:
                    groups[gid] = groups.get(gid, 0) + 1
            
            if groups:
                st.write("**그룹별 개수:**")
                for gid, count in groups.items():
                    st.write(f"- {gid}: {count}개")
        
    except Exception as e:
        st.error(f"❌ 조회 실패: {str(e)}")

st.markdown("---")

# ============================================
# 9. 디버깅: 임베딩 확인
# ============================================
st.header("9️⃣ 🔧 디버깅: 임베딩 확인")

if st.button("🔍 임베딩 NULL 체크"):
    try:
        # 임베딩이 NULL인 데이터 찾기
        result = supabase.table('test_cases').select('id, name, embedding').execute()
        
        null_count = 0
        ok_count = 0
        
        st.write(f"**총 {len(result.data)}개 검사:**")
        
        for row in result.data:
            if row['embedding'] is None:
                st.error(f"❌ ID {row['id']}: {row['name']} - 임베딩 NULL!")
                null_count += 1
            else:
                st.success(f"✅ ID {row['id']}: {row['name']} - 임베딩 OK ({len(row['embedding'])}차원)")
                ok_count += 1
        
        st.write("---")
        st.metric("임베딩 OK", f"{ok_count}개")
        st.metric("임베딩 NULL", f"{null_count}개")
        
    except Exception as e:
        st.error(f"❌ 확인 실패: {str(e)}")

st.markdown("---")

if st.button("🔍 벡터 검색 디버깅 (threshold=0)"):
    try:
        # 1. 검색어 임베딩
        search_query = "쿠폰 사용"
        
        with st.spinner("검색어 임베딩 생성 중..."):
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=search_query,
                task_type="retrieval_query"
            )
            query_embedding = result['embedding']
        
        st.success(f"✅ 검색어 임베딩: {len(query_embedding)}차원")
        
        # 2. threshold=0으로 검색 (모든 결과)
        with st.spinner("유사도 검색 중 (threshold=0)..."):
            search_result = supabase.rpc(
                'match_test_cases',
                {
                    'query_embedding': query_embedding,
                    'match_count': 100,
                    'similarity_threshold': 0.0  # ← 0으로!
                }
            ).execute()
        
        # 3. 결과 표시
        if search_result.data:
            st.success(f"✅ {len(search_result.data)}개 발견!")
            
            import pandas as pd
            df_data = []
            for item in search_result.data:
                df_data.append({
                    'id': item['id'],
                    'name': item['name'],
                    'category': item['category'],
                    'similarity': f"{item['similarity']:.4f}"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
        else:
            st.error("❌ threshold=0인데도 결과 없음!")
            st.warning("→ RPC 함수 또는 임베딩에 문제가 있습니다.")
            
    except Exception as e:
        st.error(f"❌ 검색 실패: {str(e)}")
        st.code(str(e))

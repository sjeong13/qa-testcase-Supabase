st.markdown("---")
st.header("🧪 개별 저장 테스트")

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

if st.button("🧪 그룹 저장 테스트 (3개 → 3 rows)"):
    from supabase_helpers import save_test_case_to_supabase
    
    with st.spinner("저장 중..."):
        count = save_test_case_to_supabase(test_group)
    
    if count > 0:
        st.success(f"✅ {count}개 개별 저장 완료!")
    else:
        st.error("❌ 저장 실패")

if st.button("🔍 개별 검색 테스트"):
    from supabase_helpers import search_similar_test_cases
    
    # "쿠폰 사용"으로 검색
    results = search_similar_test_cases("쿠폰 사용", limit=10)
    
    st.write(f"**검색 결과: {len(results)}개**")
    for r in results:
        st.write(f"- {r.get('name')} (유사도: {r.get('similarity', 0):.2%})")

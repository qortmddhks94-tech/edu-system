import streamlit as st
import sqlite3
import pandas as pd

# ------------------------------
# DB 연결 및 초기화
# ------------------------------
conn = sqlite3.connect("education.db", check_same_thread=False)
cur = conn.cursor()

def init_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT,
        admission_year INTEGER,
        degree_program TEXT,
        major TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        date_of_birth TEXT,
        gender TEXT,
        nationality TEXT,
        gpa REAL,
        advisor TEXT,
        enrollment_status TEXT,
        graduation_year INTEGER,
        notes TEXT,
        parent_name TEXT,
        parent_contact TEXT,
        scholarship_status TEXT,
        current_semester INTEGER,
        club TEXT,
        dormitory TEXT
    )
    """)
    conn.commit()

init_db()

# ------------------------------
# Streamlit UI
# ------------------------------
st.title("🎓 교육과정 이수 관리 시스템")

menu = st.sidebar.radio("메뉴 선택",
    ["학생 관리 (입력)", "학생 조회"])

# ------------------------------
# 학생 관리 (입력)
# ------------------------------
if menu == "학생 관리 (입력)":
    st.subheader("학생 등록")

    # 필드 입력
    student_id = st.text_input("학번")
    name = st.text_input("이름")
    admission_year = st.number_input("입학년도", step=1, min_value=2000, max_value=2100)
    degree_program = st.selectbox("학위과정", ["학사", "석사", "박사"])
    major = st.text_input("전공")
    email = st.text_input("이메일")
    phone = st.text_input("휴대폰")
    address = st.text_input("주소")
    date_of_birth = st.date_input("생년월일")
    gender = st.selectbox("성별", ["남", "여", "기타"])
    nationality = st.text_input("국적")
    gpa = st.number_input("평점(GPA)", step=0.01, min_value=0.0, max_value=4.5)
    advisor = st.text_input("지도교수")
    enrollment_status = st.selectbox("학적 상태", ["재학", "휴학", "졸업", "수료"])
    graduation_year = st.number_input("졸업년도", step=1, min_value=2000, max_value=2100)
    notes = st.text_area("비고")
    parent_name = st.text_input("보호자 이름")
    parent_contact = st.text_input("보호자 연락처")
    scholarship_status = st.selectbox("장학금 여부", ["O", "X"])
    current_semester = st.number_input("현재 학기", step=1, min_value=1, max_value=16)
    club = st.text_input("동아리")
    dormitory = st.text_input("기숙사")

    if st.button("학생 등록"):
        cur.execute("""
        INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id, name, admission_year, degree_program, major,
            email, phone, address, str(date_of_birth), gender, nationality,
            gpa, advisor, enrollment_status, graduation_year, notes,
            parent_name, parent_contact, scholarship_status, current_semester,
            club, dormitory
        ))
        conn.commit()
        st.success(f"{name} 학생이 등록되었습니다.")

    st.subheader("학생 목록 (전체)")
    df = pd.read_sql("SELECT * FROM students", conn)
    st.dataframe(df)

# ------------------------------
# 학생 조회 (요약 + 상세보기 팝업)
# ------------------------------
elif menu == "학생 조회":
    st.subheader("전체 학생 조회")

    df_students = pd.read_sql("SELECT * FROM students", conn)

    if df_students.empty:
        st.info("등록된 학생이 없습니다.")
    else:
        # 요약 정보 표시
        df_summary = df_students[["student_id", "name", "degree_program", "major"]]

        for _, row in df_summary.iterrows():
            cols = st.columns([2, 2, 2, 2, 1])
            cols[0].write(row["student_id"])
            cols[1].write(row["name"])
            cols[2].write(row["degree_program"])
            cols[3].write(row["major"])

            # 상세 조회 버튼
            if cols[4].button("상세 조회", key=f"detail_{row['student_id']}"):
                st.session_state["detail_student"] = row["student_id"]

        # 상세 정보 모달
        if "detail_student" in st.session_state:
            student_id = st.session_state["detail_student"]
            detail = df_students[df_students["student_id"] == student_id].iloc[0]

            with st.modal("학생 상세 정보"):
                st.write("### 📌 상세 정보")
                st.dataframe(pd.DataFrame(detail).T)
                if st.button("닫기"):
                    del st.session_state["detail_student"]

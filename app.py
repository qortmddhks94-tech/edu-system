import streamlit as st
import sqlite3
import pandas as pd

# ------------------------------
# DB 연결
# ------------------------------
conn = sqlite3.connect("education.db", check_same_thread=False)
cur = conn.cursor()

# ------------------------------
# DB 초기화
# ------------------------------
def init_db():
    cur.execute("""
                CREATE TABLE IF NOT EXISTS students(
        student_id TEXT PRIMARY KEY,
        name TEXT,
        admission_year INTEGER,
        degree_program TEXT,
        major TEXT
                )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        course_id TEXT PRIMARY KEY,
        course_name TEXT,
        credit INTEGER,
        year INTEGER,
        semester TEXT,
        is_required INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS programs (
        program_id TEXT PRIMARY KEY,
        program_name TEXT,
        year INTEGER,
        semester TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exchanges (
        exchange_id TEXT PRIMARY KEY,
        year INTEGER,
        round INTEGER
    )
    """)
    conn.commit()

init_db()

# ------------------------------
# Streamlit UI
# ------------------------------
st.title("🎓 교육과정 이수 관리 시스템")

menu_type = st.sidebar.radio("메뉴 구분", ["관리자용(입력)", "조회"])

# ======================================
# 1. 관리자 메뉴
# ======================================
if menu_type == "관리자용(입력)":
    menu = st.sidebar.radio("관리자 메뉴",
                            ["학생 관리", "교과목 관리", "비교과 관리", "성과교류회 관리"])

    # ------------------------------
    # 학생 관리
    # ------------------------------
    if menu == "학생 관리":
        st.subheader("학생 등록")
        student_id = st.text_input("학번")
        name = st.text_input("이름")
        admission_year = st.number_input("입학년도", step=1, min_value=2000, max_value=2100)
        degree_program = st.selectbox("학위과정", ["학사", "석사", "박사"])
        major = st.text_input("전공")

        if st.button("학생 등록"):
            cur.execute("""
                INSERT OR REPLACE INTO students (student_id, name, admission_year, degree_program, major)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, name, admission_year, degree_program, major))
            conn.commit()
            st.success(f"{name} 학생이 등록되었습니다.")

        st.subheader("학생 목록")
        df = pd.read_sql("SELECT * FROM students", conn)
        st.dataframe(df)

    # ------------------------------
    # 교과목 관리
    # ------------------------------
    elif menu == "교과목 관리":
        st.subheader("교과목 등록")
        course_id = st.text_input("과목 ID")
        course_name = st.text_input("과목명")
        credit = st.number_input("학점", step=1, min_value=1)
        year = st.number_input("개설 연도", step=1, min_value=2000, max_value=2100)
        semester = st.selectbox("학기", ["1학기", "2학기", "여름학기", "겨울학기"])
        is_required = st.checkbox("필수 과목 여부")

        if st.button("교과목 등록"):
            cur.execute("INSERT OR REPLACE INTO courses VALUES (?, ?, ?, ?, ?, ?)",
                        (course_id, course_name, credit, year, semester, int(is_required)))
            conn.commit()
            st.success(f"{course_name} 과목이 등록되었습니다.")

        st.subheader("교과목 목록")
        df = pd.read_sql("SELECT * FROM courses", conn)
        st.dataframe(df)

    # ------------------------------
    # 비교과 관리
    # ------------------------------
    elif menu == "비교과 관리":
        st.subheader("비교과 프로그램 등록")
        program_id = st.text_input("프로그램 ID")
        program_name = st.text_input("프로그램명")
        year = st.number_input("연도", step=1, min_value=2000, max_value=2100, key="program_year")
        semester = st.selectbox("학기", ["1학기", "2학기", "여름학기", "겨울학기"], key="program_sem")

        if st.button("프로그램 등록"):
            cur.execute("INSERT OR REPLACE INTO programs VALUES (?, ?, ?, ?)",
                        (program_id, program_name, year, semester))
            conn.commit()
            st.success(f"{program_name} 프로그램이 등록되었습니다.")

        st.subheader("프로그램 목록")
        df = pd.read_sql("SELECT * FROM programs", conn)
        st.dataframe(df)

    # ------------------------------
    # 성과교류회 관리
    # ------------------------------
    elif menu == "성과교류회 관리":
        st.subheader("성과교류회 등록")
        exchange_id = st.text_input("교류회 ID")
        year = st.number_input("연도", step=1, min_value=2000, max_value=2100, key="ex_year")
        round_ = st.number_input("회차", step=1, min_value=1)

        if st.button("교류회 등록"):
            cur.execute("INSERT OR REPLACE INTO exchanges VALUES (?, ?, ?)",
                        (exchange_id, year, round_))
            conn.commit()
            st.success(f"{year}년 {round_}회차 교류회가 등록되었습니다.")

        st.subheader("교류회 목록")
        df = pd.read_sql("SELECT * FROM exchanges", conn)
        st.dataframe(df)

# ======================================
# 2. 조회 메뉴
# ======================================
elif menu_type == "조회":
    menu = st.sidebar.radio("조회 메뉴", ["학생 조회", "교과과정 조회", "비교과과정 조회", "성과교류회 및 행사 조회"])

    # ------------------------------
    # 학생 조회
    # ------------------------------
    if menu == "학생 조회":
        st.subheader("전체 학생 조회")
        df_students = pd.read_sql("SELECT * FROM students", conn)

        with st.expander("🔍 검색/필터 옵션", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            search_name = col1.text_input("이름 검색")
            years = ["전체"] + sorted(df_students["admission_year"].dropna().unique().tolist())
            filter_year = col2.selectbox("입학년도", years)
            degrees = ["전체"] + df_students["degree_program"].dropna().unique().tolist()
            filter_degree = col3.selectbox("학위과정", degrees)
            majors = ["전체"] + df_students["major"].dropna().unique().tolist()
            filter_major = col4.selectbox("전공", majors)

        if search_name:
            df_students = df_students[df_students["name"].str.contains(search_name, case=False, na=False)]
        if filter_year != "전체":
            df_students = df_students[df_students["admission_year"] == filter_year]
        if filter_degree != "전체":
            df_students = df_students[df_students["degree_program"] == filter_degree]
        if filter_major != "전체":
            df_students = df_students[df_students["major"] == filter_major]

        st.write(f"총 학생 수: {len(df_students)} 명")

        for _, row in df_students.iterrows():
            cols = st.columns([2, 2, 2, 2, 1])
            cols[0].write(row["student_id"])
            cols[1].write(row["name"])
            cols[2].write(row["degree_program"])
            cols[3].write(row["major"])
            if cols[4].button("상세 조회", key=f"detail_{row['student_id']}"):
                st.session_state["popup_student"] = row.to_dict()

        if "popup_student" in st.session_state:
            student = st.session_state["popup_student"]
            with st.container():
                st.markdown(
                    f"""
                    <div style="position: fixed; top: 10%; left: 20%; width: 60%; background: white; 
                    border: 2px solid black; padding: 20px; z-index: 9999;">
                        <h3>학생 상세 정보</h3>
                        <p><b>학번:</b> {student['student_id']}</p>
                        <p><b>이름:</b> {student['name']}</p>
                        <p><b>입학년도:</b> {student['admission_year']}</p>
                        <p><b>학위과정:</b> {student['degree_program']}</p>
                        <p><b>전공:</b> {student['major']}</p>
                        <button onclick="window.location.reload()">❌ 닫기</button>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ------------------------------
    # 교과과정 조회
    # ------------------------------
    elif menu == "교과과정 조회":
        st.subheader("교과목 목록 조회")
        df_courses = pd.read_sql("SELECT * FROM courses", conn)
        st.dataframe(df_courses)

    # ------------------------------
    # 비교과과정 조회
    # ------------------------------
    elif menu == "비교과과정 조회":
        st.subheader("비교과 프로그램 조회")
        df_programs = pd.read_sql("SELECT * FROM programs", conn)
        st.dataframe(df_programs)

    # ------------------------------
    # 성과교류회 및 행사 조회
    # ------------------------------
    elif menu == "성과교류회 및 행사 조회":
        st.subheader("성과교류회 및 행사 조회")
        df_exchanges = pd.read_sql("SELECT * FROM exchanges", conn)
        st.dataframe(df_exchanges)

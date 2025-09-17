import streamlit as st
import sqlite3
import pandas as pd

# ------------------------------
# DB 연결
# ------------------------------
conn = sqlite3.connect("education.db", check_same_thread=False)
cur = conn.cursor()


# ------------------------------
# DB 초기화 함수
# ------------------------------
def init_db():
    cur.execute("""
                CREATE TABLE IF NOT EXISTS students
                (
                    student_id
                    TEXT
                    PRIMARY
                    KEY,
                    name
                    TEXT,
                    admission_year
                    INTEGER,
                    degree_program
                    TEXT,
                    major
                    TEXT,
                    email
                    TEXT,
                    phone
                    TEXT
                )
                """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS courses
                (
                    course_id
                    TEXT
                    PRIMARY
                    KEY,
                    course_name
                    TEXT,
                    credit
                    INTEGER,
                    year
                    INTEGER,
                    semester
                    TEXT,
                    is_required
                    INTEGER
                )
                """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS enrollments
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    student_id
                    TEXT,
                    course_id
                    TEXT,
                    grade
                    TEXT,
                    FOREIGN
                    KEY
                (
                    student_id
                ) REFERENCES students
                (
                    student_id
                ),
                    FOREIGN KEY
                (
                    course_id
                ) REFERENCES courses
                (
                    course_id
                )
                    )
                """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS programs
                (
                    program_id
                    TEXT
                    PRIMARY
                    KEY,
                    program_name
                    TEXT,
                    year
                    INTEGER,
                    semester
                    TEXT
                )
                """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS program_participation
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    student_id
                    TEXT,
                    program_id
                    TEXT,
                    FOREIGN
                    KEY
                (
                    student_id
                ) REFERENCES students
                (
                    student_id
                ),
                    FOREIGN KEY
                (
                    program_id
                ) REFERENCES programs
                (
                    program_id
                )
                    )
                """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS exchanges
                (
                    exchange_id
                    TEXT
                    PRIMARY
                    KEY,
                    year
                    INTEGER,
                    round
                    INTEGER
                )
                """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS exchange_attendance
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    student_id
                    TEXT,
                    exchange_id
                    TEXT,
                    FOREIGN
                    KEY
                (
                    student_id
                ) REFERENCES students
                (
                    student_id
                ),
                    FOREIGN KEY
                (
                    exchange_id
                ) REFERENCES exchanges
                (
                    exchange_id
                )
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
                            ["학생 관리", "교과목 관리", "비교과 관리", "성과교류회 관리", "조건 검증"])

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
        email = st.text_input("이메일")
        phone = st.text_input("휴대폰")

        if st.button("학생 등록"):
            cur.execute("""
                INSERT OR REPLACE INTO students
                (student_id, name, admission_year, degree_program, major, email, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, name, admission_year, degree_program, major, email, phone))
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
            cur.execute("""
                INSERT OR REPLACE INTO courses
                (course_id, course_name, credit, year, semester, is_required)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (course_id, course_name, credit, year, semester, int(is_required)))
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
            cur.execute("""
                INSERT OR REPLACE INTO programs
                (program_id, program_name, year, semester)
                VALUES (?, ?, ?, ?)
            """, (program_id, program_name, year, semester))
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
            cur.execute("""
                INSERT OR REPLACE INTO exchanges
                (exchange_id, year, round)
                VALUES (?, ?, ?)
            """, (exchange_id, year, round_))
            conn.commit()
            st.success(f"{year}년 {round_}회차 교류회가 등록되었습니다.")

        st.subheader("교류회 목록")
        df = pd.read_sql("SELECT * FROM exchanges", conn)
        st.dataframe(df)

    # ------------------------------
    # 조건 검증
    # ------------------------------
    elif menu == "조건 검증":
        st.subheader("조건 검증")
        student_id = st.text_input("학번 입력")

        if st.button("검증하기"):
            query = """
                    SELECT IFNULL(SUM(c.credit), 0)                           as total_credit,
                           SUM(CASE WHEN c.is_required = 1 THEN 1 ELSE 0 END) as required_count
                    FROM enrollments e
                             JOIN courses c ON e.course_id = c.course_id
                    WHERE e.student_id = ? \
                    """
            result = cur.execute(query, (student_id,)).fetchone()
            total_credit, required_count = result if result else (0, 0)

            program_count = \
            cur.execute("SELECT COUNT(*) FROM program_participation WHERE student_id=?", (student_id,)).fetchone()[0]
            exchange_count = \
            cur.execute("SELECT COUNT(*) FROM exchange_attendance WHERE student_id=?", (student_id,)).fetchone()[0]

            st.write(f"총 이수 학점: {total_credit}")
            st.write(f"필수 과목 이수 수: {required_count}")
            st.write(f"비교과 참여 횟수: {program_count}")
            st.write(f"성과교류회 참여 횟수: {exchange_count}")

            if total_credit >= 12 and program_count >= 4 and exchange_count >= 2:
                st.success("✅ 교육과정 이수 조건 충족")
            else:
                st.error("❌ 조건 미충족")

# ======================================
# 2. 조회 메뉴
# ======================================
elif menu_type == "조회":
    menu = st.sidebar.radio("조회 메뉴",
                            ["학생 조회", "교과과정 조회", "비교과과정 조회", "성과교류회 및 행사 조회"])

    # ------------------------------
    # 학생 조회
    # ------------------------------
    if menu == "학생 조회":
        st.subheader("전체 학생 조회")
        df_students = pd.read_sql("SELECT * FROM students", conn)

        if df_students.empty:
            st.info("등록된 학생이 없습니다.")
        else:
            # 필터링 UI
            with st.expander("🔍 검색/필터 옵션", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                search_name = col1.text_input("이름 검색")
                years = ["전체"] + sorted(df_students["admission_year"].dropna().unique().tolist())
                filter_year = col2.selectbox("입학년도", years)
                degrees = ["전체"] + df_students["degree_program"].dropna().unique().tolist()
                filter_degree = col3.selectbox("학위과정", degrees)
                majors = ["전체"] + df_students["major"].dropna().unique().tolist()
                filter_major = col4.selectbox("전공", majors)

            # 필터 적용
            if search_name:
                df_students = df_students[df_students["name"].str.contains(search_name, case=False, na=False)]
            if filter_year != "전체":
                df_students = df_students[df_students["admission_year"] == filter_year]
            if filter_degree != "전체":
                df_students = df_students[df_students["degree_program"] == filter_degree]
            if filter_major != "전체":
                df_students = df_students[df_students["major"] == filter_major]

            # 요약 데이터 표시
            df_summary = df_students[["student_id", "name", "degree_program", "major"]]
            st.dataframe(df_summary)

            # 상세 조회
            selected_id = st.selectbox("상세조회할 학생 선택 (학번)", ["선택 안 함"] + df_summary["student_id"].tolist())
            if selected_id != "선택 안 함":
                detail = df_students[df_students["student_id"] == selected_id]
                st.write("### 📌 상세 학생 정보")
                st.dataframe(detail)

    # ------------------------------
    # 교과과정 조회
    # ------------------------------
    elif menu == "교과과정 조회":
        st.subheader("교과목 목록 조회")
        df_courses = pd.read_sql("SELECT * FROM courses", conn)

        if df_courses.empty:
            st.info("등록된 교과목이 없습니다.")
        else:
            with st.expander("🔍 검색/필터 옵션", expanded=True):
                col1, col2, col3 = st.columns(3)
                years = ["전체"] + sorted(df_courses["year"].dropna().unique().tolist())
                filter_year = col1.selectbox("개설 연도", years)
                semesters = ["전체"] + df_courses["semester"].dropna().unique().tolist()
                filter_semester = col2.selectbox("학기", semesters)
                required_opts = ["전체", "필수", "선택"]
                filter_required = col3.selectbox("필수 여부", required_opts)

            if filter_year != "전체":
                df_courses = df_courses[df_courses["year"] == filter_year]
            if filter_semester != "전체":
                df_courses = df_courses[df_courses["semester"] == filter_semester]
            if filter_required != "전체":
                df_courses = df_courses[df_courses["is_required"] == (1 if filter_required == "필수" else 0)]

            df_summary = df_courses[["course_id", "course_name", "credit", "year", "semester", "is_required"]]
            st.dataframe(df_summary)

            selected_id = st.selectbox("상세조회할 교과목 선택 (ID)", ["선택 안 함"] + df_summary["course_id"].tolist())
            if selected_id != "선택 안 함":
                detail = df_courses[df_courses["course_id"] == selected_id]
                st.write("### 📌 상세 교과목 정보")
                st.dataframe(detail)

    # ------------------------------
    # 비교과과정 조회
    # ------------------------------
    elif menu == "비교과과정 조회":
        st.subheader("비교과 프로그램 조회")
        df_programs = pd.read_sql("SELECT * FROM programs", conn)

        if df_programs.empty:
            st.info("등록된 비교과 프로그램이 없습니다.")
        else:
            with st.expander("🔍 검색/필터 옵션", expanded=True):
                col1, col2 = st.columns(2)
                years = ["전체"] + sorted(df_programs["year"].dropna().unique().tolist())
                filter_year = col1.selectbox("연도", years)
                semesters = ["전체"] + df_programs["semester"].dropna().unique().tolist()
                filter_semester = col2.selectbox("학기", semesters)

            if filter_year != "전체":
                df_programs = df_programs[df_programs["year"] == filter_year]
            if filter_semester != "전체":
                df_programs = df_programs[df_programs["semester"] == filter_semester]

            df_summary = df_programs[["program_id", "program_name", "year", "semester"]]
            st.dataframe(df_summary)

            selected_id = st.selectbox("상세조회할 프로그램 선택 (ID)", ["선택 안 함"] + df_summary["program_id"].tolist())
            if selected_id != "선택 안 함":
                detail = df_programs[df_programs["program_id"] == selected_id]
                st.write("### 📌 상세 프로그램 정보")
                st.dataframe(detail)

    # ------------------------------
    # 성과교류회 조회
    # ------------------------------
    elif menu == "성과교류회 및 행사 조회":
        st.subheader("성과교류회 및 행사 조회")
        df_exchanges = pd.read_sql("SELECT * FROM exchanges", conn)

        if df_exchanges.empty:
            st.info("등록된 성과교류회가 없습니다.")
        else:
            with st.expander("🔍 검색/필터 옵션", expanded=True):
                col1, col2 = st.columns(2)
                years = ["전체"] + sorted(df_exchanges["year"].dropna().unique().tolist())
                filter_year = col1.selectbox("연도", years)
                rounds = ["전체"] + sorted(df_exchanges["round"].dropna().unique().tolist())
                filter_round = col2.selectbox("회차", rounds)

            if filter_year != "전체":
                df_exchanges = df_exchanges[df_exchanges["year"] == filter_year]
            if filter_round != "전체":
                df_exchanges = df_exchanges[df_exchanges["round"] == filter_round]

            df_summary = df_exchanges[["exchange_id", "year", "round"]]
            st.dataframe(df_summary)

            selected_id = st.selectbox("상세조회할 교류회 선택 (ID)", ["선택 안 함"] + df_summary["exchange_id"].tolist())
            if selected_id != "선택 안 함":
                detail = df_exchanges[df_exchanges["exchange_id"] == selected_id]
                st.write("### 📌 상세 교류회 정보")
                st.dataframe(detail)

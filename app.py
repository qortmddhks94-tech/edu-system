import streamlit as st
import sqlite3
import pandas as pd
import io
import datetime

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
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        course_id TEXT,
        grade TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(course_id) REFERENCES courses(course_id)
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
    CREATE TABLE IF NOT EXISTS program_participation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        program_id TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(program_id) REFERENCES programs(program_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exchanges (
        exchange_id TEXT PRIMARY KEY,
        year INTEGER,
        round INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exchange_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        exchange_id TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(exchange_id) REFERENCES exchanges(exchange_id)
    )
    """)
    conn.commit()


init_db()

# ------------------------------
# Streamlit UI
# ------------------------------
st.title("🎓 교육과정 이수 관리 시스템")

menu = st.sidebar.radio(
    "메뉴 선택",
    ["학생 관리", "교과목 관리", "비교과 관리", "성과교류회 관리", "조건 검증", "데이터 내보내기"]
)

# ------------------------------
# 학생 관리
# ------------------------------
if menu == "학생 관리":
    st.subheader("학생 등록")
    student_id = st.text_input("학번")
    name = st.text_input("이름")
    admission_year = st.number_input("입학년도", step=1, min_value=2000, max_value=2100)
    major = st.text_input("전공")

    if st.button("학생 등록"):
        cur.execute("INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?)",
                    (student_id, name, admission_year, major))
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

# ------------------------------
# 조건 검증
# ------------------------------
elif menu == "조건 검증":
    st.subheader("조건 검증")
    student_id = st.text_input("학번 입력")

    if st.button("검증하기"):
        # 교과목 이수 학점 계산
        query = """
        SELECT IFNULL(SUM(c.credit),0) as total_credit,
               SUM(CASE WHEN c.is_required=1 THEN 1 ELSE 0 END) as required_count
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = ?
        """
        result = cur.execute(query, (student_id,)).fetchone()
        total_credit, required_count = result if result else (0, 0)

        # 비교과 참여 횟수
        program_count = cur.execute(
            "SELECT COUNT(*) FROM program_participation WHERE student_id=?",
            (student_id,)
        ).fetchone()[0]

        # 성과교류회 참여 횟수
        exchange_count = cur.execute(
            "SELECT COUNT(*) FROM exchange_attendance WHERE student_id=?",
            (student_id,)
        ).fetchone()[0]

        st.write(f"총 이수 학점: {total_credit}")
        st.write(f"필수 과목 이수 수: {required_count}")
        st.write(f"비교과 참여 횟수: {program_count}")
        st.write(f"성과교류회 참여 횟수: {exchange_count}")

        # 조건 판정
        if total_credit >= 12 and program_count >= 4 and exchange_count >= 2:
            st.success("✅ 교육과정 이수 조건 충족")
        else:
            st.error("❌ 조건 미충족")

# ------------------------------
# 데이터 내보내기
# ------------------------------
elif menu == "데이터 내보내기":
    st.subheader("📂 엑셀 파일로 데이터 다운로드")

    # 메모리 버퍼 생성
    output = io.BytesIO()

    # 엑셀 파일 작성
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_students = pd.read_sql("SELECT * FROM students", conn)
        df_students.to_excel(writer, index=False, sheet_name="students")

        df_courses = pd.read_sql("SELECT * FROM courses", conn)
        df_courses.to_excel(writer, index=False, sheet_name="courses")

        df_programs = pd.read_sql("SELECT * FROM programs", conn)
        df_programs.to_excel(writer, index=False, sheet_name="programs")

        df_exchanges = pd.read_sql("SELECT * FROM exchanges", conn)
        df_exchanges.to_excel(writer, index=False, sheet_name="exchanges")

    # 다운로드 버튼
    st.download_button(
        label="📥 엑셀 다운로드",
        data=output.getvalue(),
        file_name=f"edu_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
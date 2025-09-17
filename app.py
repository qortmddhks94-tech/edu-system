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
    # 학생 정보 (field1 → degree_program)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT,
        admission_year INTEGER,
        major TEXT,
        degree_program TEXT,
        field2 TEXT,
        field3 TEXT,
        field4 TEXT,
        field5 TEXT,
        field6 TEXT,
        field7 TEXT,
        field8 TEXT,
        field9 TEXT,
        field10 TEXT,
        field11 TEXT,
        field12 TEXT,
        field13 TEXT,
        field14 TEXT,
        field15 TEXT,
        field16 TEXT
    )
    """)
    # 교과목
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
    # 학생 수강 내역
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
    # 비교과 프로그램
    cur.execute("""
    CREATE TABLE IF NOT EXISTS programs (
        program_id TEXT PRIMARY KEY,
        program_name TEXT,
        year INTEGER,
        semester TEXT
    )
    """)
    # 비교과 참여 내역
    cur.execute("""
    CREATE TABLE IF NOT EXISTS program_participation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        program_id TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(program_id) REFERENCES programs(program_id)
    )
    """)
    # 성과교류회
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exchanges (
        exchange_id TEXT PRIMARY KEY,
        year INTEGER,
        round INTEGER
    )
    """)
    # 성과교류회 참여 내역
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
    ["학생 관리", "교과목 관리", "비교과 관리", "성과교류회 관리", "조건 검증"]
)

# ------------------------------
# 학생 관리
# ------------------------------
if menu == "학생 관리":
    st.subheader("학생 등록")

    # 기본 항목
    student_id = st.text_input("학번")
    name = st.text_input("이름")
    admission_year = st.number_input("입학년도", step=1, min_value=2000, max_value=2100)
    major = st.text_input("전공")

    # degree_program은 선택박스
    degree_program = st.selectbox("학위과정", ["학사", "석사", "박사"])

    # 확장 항목 (field2 ~ field16)
    extra_fields = []
    for i in range(2, 17):
        extra_fields.append(st.text_input(f"추가 항목 {i}"))

    if st.button("학생 등록"):
        cur.execute("""
            INSERT OR REPLACE INTO students VALUES (
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (student_id, name, admission_year, major,
              degree_program, *extra_fields))
        conn.commit()
        st.success(f"{name} 학생이 등록되었습니다.")

    st.subheader("학생 목록")
    df = pd.read_sql("SELECT * FROM students", conn)
    st.dataframe(df)

    # 학생 엑셀 다운로드
    st.markdown("### 📂 학생 데이터 엑셀 다운로드")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="students")
    st.download_button(
        label="📥 학생 엑셀 다운로드",
        data=output.getvalue(),
        file_name=f"students_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 학생 엑셀 업로드
    st.markdown("### 📤 학생 데이터 엑셀 업로드 (덮어쓰기)")
    uploaded_file = st.file_uploader("학생 엑셀 업로드", type=["xlsx"], key="upload_students")
    if uploaded_file is not None:
        df_uploaded = pd.read_excel(uploaded_file)
        cur.execute("DELETE FROM students")
        df_uploaded.to_sql("students", conn, if_exists="append", index=False)
        conn.commit()
        st.success("✅ 학생 데이터가 엑셀로 덮어쓰기 되었습니다!")

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

    # 교과목 엑셀 다운로드
    st.markdown("### 📂 교과목 데이터 엑셀 다운로드")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="courses")
    st.download_button(
        label="📥 교과목 엑셀 다운로드",
        data=output.getvalue(),
        file_name=f"courses_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 교과목 엑셀 업로드
    st.markdown("### 📤 교과목 데이터 엑셀 업로드 (덮어쓰기)")
    uploaded_file = st.file_uploader("교과목 엑셀 업로드", type=["xlsx"], key="upload_courses")
    if uploaded_file is not None:
        df_uploaded = pd.read_excel(uploaded_file)
        cur.execute("DELETE FROM courses")
        df_uploaded.to_sql("courses", conn, if_exists="append", index=False)
        conn.commit()
        st.success("✅ 교과목 데이터가 엑셀로 덮어쓰기 되었습니다!")

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

    # 비교과 엑셀 다운로드
    st.markdown("### 📂 비교과 데이터 엑셀 다운로드")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="programs")
    st.download_button(
        label="📥 비교과 엑셀 다운로드",
        data=output.getvalue(),
        file_name=f"programs_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 비교과 엑셀 업로드
    st.markdown("### 📤 비교과 데이터 엑셀 업로드 (덮어쓰기)")
    uploaded_file = st.file_uploader("비교과 엑셀 업로드", type=["xlsx"], key="upload_programs")
    if uploaded_file is not None:
        df_uploaded = pd.read_excel(uploaded_file)
        cur.execute("DELETE FROM programs")
        df_uploaded.to_sql("programs", conn, if_exists="append", index=False)
        conn.commit()
        st.success("✅ 비교과 데이터가 엑셀로 덮어쓰기 되었습니다!")

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

    # 성과교류회 엑셀 다운로드
    st.markdown("### 📂 성과교류회 데이터 엑셀 다운로드")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="exchanges")
    st.download_button(
        label="📥 성과교류회 엑셀 다운로드",
        data=output.getvalue(),
        file_name=f"exchanges_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 성과교류회 엑셀 업로드
    st.markdown("### 📤 성과교류회 데이터 엑셀 업로드 (덮어쓰기)")
    uploaded_file = st.file_uploader("성과교류회 엑셀 업로드", type=["xlsx"], key="upload_exchanges")
    if uploaded_file is not None:
        df_uploaded = pd.read_excel(uploaded_file)
        cur.execute("DELETE FROM exchanges")
        df_uploaded.to_sql("exchanges", conn, if_exists="append", index=False)
        conn.commit()
        st.success("✅ 성과교류회 데이터가 엑셀로 덮어쓰기 되었습니다!")

# ------------------------------
# 조건 검증
# ------------------------------
elif menu == "조건 검증":
    st.subheader("조건 검증")
    student_id = st.text_input("학번 입력")

    if st.button("검증하기"):
        query = """
        SELECT IFNULL(SUM(c.credit),0) as total_credit,
               SUM(CASE WHEN c.is_required=1 THEN 1 ELSE 0 END) as required_count
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = ?
        """
        result = cur.execute(query, (student_id,)).fetchone()
        total_credit, required_count = result if result else (0, 0)

        program_count = cur.execute(
            "SELECT COUNT(*) FROM program_participation WHERE student_id=?",
            (student_id,)
        ).fetchone()[0]

        exchange_count = cur.execute(
            "SELECT COUNT(*) FROM exchange_attendance WHERE student_id=?",
            (student_id,)
        ).fetchone()[0]

        st.write(f"총 이수 학점: {total_credit}")
        st.write(f"필수 과목 이수 수: {required_count}")
        st.write(f"비교과 참여 횟수: {program_count}")
        st.write(f"성과교류회 참여 횟수: {exchange_count}")

        if total_credit >= 12 and program_count >= 4 and exchange_count >= 2:
            st.success("✅ 교육과정 이수 조건 충족")
        else:
            st.error("❌ 조건 미충족")

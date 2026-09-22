import random
from datetime import date, datetime, time, timedelta

import mysql.connector

from config import Config


RANDOM_SEED = 20260219


def day_code_from_date(d: date) -> str:
    return {
        0: "MON",
        1: "TUE",
        2: "WED",
        3: "THU",
        4: "FRI",
        5: "SAT",
    }.get(d.weekday(), "SUN")


def to_time_obj(value):
    if isinstance(value, time):
        return value
    if isinstance(value, timedelta):
        return (datetime.min + value).time()
    if isinstance(value, str):
        return datetime.strptime(value, "%H:%M:%S").time()
    raise ValueError(f"Unsupported time value: {value!r}")


def clear_data(cur):
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    cur.execute("DELETE FROM attendance")
    cur.execute("DELETE FROM lectures")
    cur.execute("DELETE FROM timetable")
    cur.execute("DELETE FROM students")
    cur.execute("DELETE FROM faculty")
    cur.execute("DELETE FROM admins")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")


def ensure_university(cur):
    cur.execute("SELECT 1 FROM universities WHERE university_id = 1 LIMIT 1")
    if cur.fetchone():
        return
    cur.execute(
        """
        INSERT INTO universities (
            university_id,
            university_name,
            domain,
            registered_address,
            official_contact_email,
            official_contact_phone,
            website_url,
            plan,
            is_active
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            1,
            "LJ University",
            "lj.edu",
            "Sarkhej, Ahmedabad, Gujarat, India",
            "info@lj.edu",
            "+91-79-12345678",
            "https://www.lj.edu",
            "PREMIUM",
            True,
        ),
    )


def insert_admin(cur):
    cur.execute(
        """
        INSERT INTO admins (university_id, name, email, password_hash, is_verified)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            1,
            "Dr. Rajesh Patel",
            "admin@lj.edu",
            "$2b$12$VfP8sD1Q2xH7mN3rK9tL4wY6zA0cE5uI8oP2qR7sT1vW6xY9zB3Cd",
            True,
        ),
    )


def insert_faculty(cur):
    faculty_rows = [
        (
            1,
            "Dr. Nidhi Shah",
            "nidhi.shah@lj.edu",
            "Computer Engineering",
            "$2b$12$Jq7rT4mK9pL2vX5zC8nH1sD6fG3aQ0wE7uI4oP9yR2tV5bN8mL1Kc",
            True,
        ),
        (
            1,
            "Prof. Amit Trivedi",
            "amit.trivedi@lj.edu",
            "Information Technology",
            "$2b$12$M8nV2kP5xR9tD3sF6gH1jL4qW7zC0bE5uI2oY8aT3rN6mK9pQ1vXf",
            True,
        ),
        (
            1,
            "Prof. Suresh Chauhan",
            "suresh.chauhan@lj.edu",
            "Mechanical",
            "$2b$12$R3tY7uI1oP6aS9dF2gH5jK8lZ0xC4vB7nM1qW5eR9tY2uI6oP3aSd",
            True,
        ),
    ]
    cur.executemany(
        """
        INSERT INTO faculty (university_id, name, email, department, password_hash, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        faculty_rows,
    )

    cur.execute("SELECT faculty_id, email FROM faculty WHERE university_id = 1")
    ids_by_email = {row["email"]: row["faculty_id"] for row in cur.fetchall()}
    return {
        "ce": ids_by_email["nidhi.shah@lj.edu"],
        "it": ids_by_email["amit.trivedi@lj.edu"],
        "me": ids_by_email["suresh.chauhan@lj.edu"],
    }


def insert_students(cur):
    students = [
        (1, "LJCE33001", "Aarav Mehta", "Computer Engineering", 3, "aarav.mehta@lj.edu", "$2b$12$kL9pQ3rT7vX1mN5bC8dF2gH6jK0lZ4xC7vB1nM5qW8eR2tY6uI3oP", True),
        (1, "LJCE33002", "Krish Shah", "Computer Engineering", 3, "krish.shah@lj.edu", "$2b$12$pQ4rT8vX2mN6bC9dF3gH7jK1lZ5xC8vB2nM6qW9eR3tY7uI4oP1aS", True),
        (1, "LJCE33003", "Dhruv Desai", "Computer Engineering", 3, "dhruv.desai@lj.edu", "$2b$12$rT5vX9mN3bC7dF1gH4jK8lZ2xC6vB9nM3qW7eR1tY8uI5oP2aS6d", True),
        (1, "LJIT33001", "Pranav Joshi", "Information Technology", 3, "pranav.joshi@lj.edu", "$2b$12$vX6mN1bC4dF8gH2jK5lZ9xC3vB7nM1qW8eR2tY9uI6oP3aS7dF0g", True),
        (1, "LJIT33002", "Neil Trivedi", "Information Technology", 3, "neil.trivedi@lj.edu", "$2b$12$mN7bC2dF5gH9jK3lZ6xC0vB4nM8qW2eR9tY3uI0oP7aS4dF1gH5j", True),
        (1, "LJME33001", "Vivek Parmar", "Mechanical", 3, "vivek.parmar@lj.edu", "$2b$12$bC8dF3gH6jK0lZ4xC7vB1nM5qW8eR2tY6uI3oP9aS5dF2gH7jK1l", True),
        (1, "LJME33002", "Rohan Solanki", "Mechanical", 3, "rohan.solanki@lj.edu", "$2b$12$dF9gH4jK7lZ1xC5vB8nM2qW6eR0tY3uI7oP4aS0dF6gH3jK8lZ2x", True),
        (1, "LJCE55001", "Aniket Patel", "Computer Engineering", 5, "aniket.patel@lj.edu", "$2b$12$gH1jK5lZ8xC2vB6nM9qW3eR7tY1uI8oP5aS1dF7gH4jK9lZ3xC6v", True),
        (1, "LJCE55002", "Yash Gohil", "Computer Engineering", 5, "yash.gohil@lj.edu", "$2b$12$jK2lZ6xC9vB3nM7qW0eR4tY8uI2oP9aS6dF2gH8jK5lZ0xC7vB1n", True),
        (1, "LJCE55003", "Manan Bhatt", "Computer Engineering", 5, "manan.bhatt@lj.edu", "$2b$12$lZ3xC7vB1nM8qW2eR5tY9uI3oP0aS7dF3gH9jK6lZ1xC8vB2nM4q", True),
        (1, "LJIT55001", "Kunal Dave", "Information Technology", 5, "kunal.dave@lj.edu", "$2b$12$xC4vB8nM2qW9eR3tY6uI0oP4aS1dF8gH4jK0lZ7xC2vB9nM3qW5e", True),
        (1, "LJIT55002", "Om Vyas", "Information Technology", 5, "om.vyas@lj.edu", "$2b$12$vB5nM9qW3eR0tY4uI7oP1aS2dF9gH5jK1lZ8xC3vB0nM4qW6eR2t", True),
        (1, "LJME55001", "Nikhil Chauhan", "Mechanical", 5, "nikhil.chauhan@lj.edu", "$2b$12$nM6qW0eR4tY1uI5oP8aS3dF0gH6jK2lZ9xC4vB1nM5qW7eR3tY6u", True),
        (1, "LJME55002", "Tushar Rana", "Mechanical", 5, "tushar.rana@lj.edu", "$2b$12$qW7eR1tY5uI2oP6aS9dF4gH1jK7lZ3xC0vB5nM2qW8eR4tY7uI0o", True),
        (1, "LJCE77001", "Harsh Modi", "Computer Engineering", 7, "harsh.modi@lj.edu", "$2b$12$eR8tY2uI6oP3aS7dF0gH5jK2lZ8xC4vB1nM6qW3eR9tY5uI8oP1a", True),
        (1, "LJCE77002", "Rahul Barot", "Computer Engineering", 7, "rahul.barot@lj.edu", "$2b$12$tY9uI3oP7aS4dF1gH6jK3lZ9xC5vB2nM7qW4eR0tY6uI9oP2aS5d", True),
        (1, "LJIT77001", "Devansh Thakkar", "Information Technology", 7, "devansh.thakkar@lj.edu", "$2b$12$uI0oP4aS8dF5gH2jK7lZ4xC0vB3nM8qW5eR1tY7uI0oP3aS6dF9g", True),
        (1, "LJIT77002", "Smit Pandya", "Information Technology", 7, "smit.pandya@lj.edu", "$2b$12$oP1aS5dF9gH6jK3lZ8xC1vB4nM9qW6eR2tY8uI1oP4aS7dF0gH3j", True),
        (1, "LJME77001", "Aditya Jhala", "Mechanical", 7, "aditya.jhala@lj.edu", "$2b$12$aS2dF6gH0jK7lZ4xC9vB2nM5qW0eR7tY3uI9oP2aS5dF8gH1jK4l", True),
        (1, "LJME77002", "Kartik Zala", "Mechanical", 7, "kartik.zala@lj.edu", "$2b$12$S3dF7gH1jK8lZ5xC0vB3nM6qW1eR8tY4uI0oP3aS6dF9gH2jK5lZ", True),
    ]
    cur.executemany(
        """
        INSERT INTO students (
            university_id, enrollment_no, name, department, semester, email, password_hash, is_active
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        students,
    )
    cur.execute("SELECT student_id, enrollment_no FROM students WHERE university_id = 1")
    return {row["enrollment_no"]: row["student_id"] for row in cur.fetchall()}


def insert_timetable(cur, faculty_ids):
    base_entries = [
        ("Computer Engineering", 3, "Data Structures", "MON", "09:00:00", "10:00:00", faculty_ids["ce"], False),
        ("Information Technology", 5, "DBMS", "MON", "10:15:00", "11:15:00", faculty_ids["it"], False),
        ("Computer Engineering", 5, "Operating Systems", "TUE", "09:00:00", "10:00:00", faculty_ids["ce"], False),
        ("Mechanical", 3, "Mathematics", "TUE", "11:00:00", "12:00:00", faculty_ids["me"], False),
        ("Information Technology", 7, "Computer Networks", "WED", "10:15:00", "11:15:00", faculty_ids["it"], False),
        ("Computer Engineering", 7, "DBMS", "THU", "09:00:00", "10:00:00", faculty_ids["ce"], False),
        ("Mechanical", 5, "Thermodynamics", "THU", "11:00:00", "12:00:00", faculty_ids["me"], False),
        ("Computer Engineering", 3, "Operating Systems", "FRI", "09:00:00", "10:00:00", faculty_ids["ce"], False),
        ("Information Technology", 3, "Data Structures", "FRI", "10:15:00", "11:15:00", faculty_ids["it"], False),
        ("Mechanical", 7, "Thermodynamics", "FRI", "11:30:00", "12:30:00", faculty_ids["me"], False),
        ("Mechanical", 5, "Mathematics", "SAT", "09:30:00", "10:30:00", faculty_ids["me"], False),
        ("Computer Engineering", 7, "Computer Networks", "SAT", "10:45:00", "11:45:00", faculty_ids["ce"], False),
        ("Computer Engineering", 5, "Computer Networks", "FRI", "13:30:00", "14:30:00", faculty_ids["ce"], True),
        ("Information Technology", 7, "Mathematics", "FRI", "14:45:00", "15:45:00", faculty_ids["it"], True),
    ]

    cur.executemany(
        """
        INSERT INTO timetable (
            university_id, faculty_id, department, semester, subject, day, start_time, end_time
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (1, fac_id, dept, sem, subject, day, start, end)
            for (dept, sem, subject, day, start, end, fac_id, _extra) in base_entries
        ],
    )

    cur.execute(
        """
        SELECT
            timetable_id, faculty_id, department, semester, subject, day,
            start_time,
            end_time
        FROM timetable
        WHERE university_id = 1
        """
    )
    rows = cur.fetchall()
    index = {
        (
            r["faculty_id"],
            r["department"],
            r["semester"],
            r["subject"],
            r["day"],
            to_time_obj(r["start_time"]).strftime("%H:%M:%S"),
            to_time_obj(r["end_time"]).strftime("%H:%M:%S"),
        ): r["timetable_id"]
        for r in rows
    }

    timetable = []
    for dept, sem, subject, day, start, end, fac_id, extra in base_entries:
        key = (fac_id, dept, sem, subject, day, start, end)
        timetable.append(
            {
                "timetable_id": index[key],
                "faculty_id": fac_id,
                "department": dept,
                "semester": sem,
                "subject": subject,
                "day": day,
                "start_time": start,
                "end_time": end,
                "extra_friday": extra,
            }
        )
    return timetable


def insert_lectures(cur, timetable_rows):
    today = date.today()
    last_30_days = [today - timedelta(days=i) for i in range(30)]
    last_4_fridays = [d for d in last_30_days if d.weekday() == 4][:4]
    last_4_fridays_set = set(last_4_fridays)

    lecture_values = []
    for d in last_30_days:
        if d.weekday() == 6:
            continue
        day_code = day_code_from_date(d)
        for slot in timetable_rows:
            if slot["day"] != day_code:
                continue
            if slot["extra_friday"] and d not in last_4_fridays_set:
                continue
            start_dt = datetime.combine(d, to_time_obj(slot["start_time"]))
            end_dt = datetime.combine(d, to_time_obj(slot["end_time"]))
            lecture_values.append((slot["timetable_id"], d, "MARKED", start_dt, end_dt))

    cur.executemany(
        """
        INSERT INTO lectures (timetable_id, lecture_date, status, started_at, ended_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        lecture_values,
    )
    return len(lecture_values)


def get_students_by_class(cur):
    cur.execute(
        """
        SELECT student_id, department, semester
        FROM students
        WHERE university_id = 1 AND is_active = TRUE
        """
    )
    grouped = {}
    for row in cur.fetchall():
        key = (row["department"], row["semester"])
        grouped.setdefault(key, []).append(row["student_id"])
    return grouped


def insert_attendance(cur, low_ids, high_ids):
    students_by_class = get_students_by_class(cur)
    cur.execute(
        """
        SELECT
            l.lecture_id,
            l.lecture_date,
            t.department,
            t.semester,
            t.day,
            t.start_time AS start_time
        FROM lectures l
        JOIN timetable t ON t.timetable_id = l.timetable_id
        WHERE l.status = 'MARKED'
        ORDER BY l.lecture_id ASC
        """
    )
    lectures = cur.fetchall()

    low_set = set(low_ids)
    high_set = set(high_ids)

    attendance_values = []
    for lec in lectures:
        key = (lec["department"], lec["semester"])
        student_ids = students_by_class.get(key, [])
        if not student_ids:
            continue

        rng = random.Random(RANDOM_SEED + int(lec["lecture_id"]))
        if lec["day"] == "FRI":
            target_pct = rng.randint(75, 95)
        else:
            target_pct = rng.randint(65, 85)

        total = len(student_ids)
        present_count = int(round((target_pct / 100.0) * total))
        present_count = max(0, min(total, present_count))

        scored = []
        for sid in student_ids:
            score = rng.random()
            if sid in high_set:
                score += 1.0
            elif sid in low_set:
                score -= 1.0
            scored.append((score, sid))
        scored.sort(reverse=True)
        present_ids = {sid for _score, sid in scored[:present_count]}

        mark_base = datetime.combine(lec["lecture_date"], to_time_obj(lec["start_time"]))
        for sid in student_ids:
            status = "PRESENT" if sid in present_ids else "ABSENT"
            marked_at = mark_base + timedelta(minutes=5 + rng.randint(0, 20))
            attendance_values.append((lec["lecture_id"], sid, status, marked_at))

    cur.executemany(
        """
        INSERT INTO attendance (lecture_id, student_id, status, marked_at)
        VALUES (%s, %s, %s, %s)
        """,
        attendance_values,
    )
    return len(attendance_values)


def get_student_pct(cur, student_id):
    cur.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
            COUNT(*) AS total_count
        FROM attendance
        WHERE student_id = %s
        """,
        (student_id,),
    )
    row = cur.fetchone()
    total = int(row["total_count"] or 0)
    present = int(row["present_count"] or 0)
    return (present * 100.0 / total) if total > 0 else 0.0


def enforce_thresholds(cur, low_ids, high_ids):
    for sid in low_ids:
        while get_student_pct(cur, sid) >= 65.0:
            cur.execute(
                """
                SELECT attendance_id
                FROM attendance
                WHERE student_id = %s AND status = 'PRESENT'
                ORDER BY attendance_id DESC
                LIMIT 1
                """,
                (sid,),
            )
            row = cur.fetchone()
            if not row:
                break
            cur.execute("UPDATE attendance SET status = 'ABSENT' WHERE attendance_id = %s", (row["attendance_id"],))

    for sid in high_ids:
        while get_student_pct(cur, sid) <= 85.0:
            cur.execute(
                """
                SELECT attendance_id
                FROM attendance
                WHERE student_id = %s AND status = 'ABSENT'
                ORDER BY attendance_id DESC
                LIMIT 1
                """,
                (sid,),
            )
            row = cur.fetchone()
            if not row:
                break
            cur.execute("UPDATE attendance SET status = 'PRESENT' WHERE attendance_id = %s", (row["attendance_id"],))


def main():
    conn = None
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT,
            database=Config.MYSQL_DATABASE,
        )
        conn.start_transaction()
        cur = conn.cursor(dictionary=True)

        clear_data(cur)
        ensure_university(cur)
        insert_admin(cur)
        faculty_ids = insert_faculty(cur)
        students_by_enrollment = insert_students(cur)
        timetable_rows = insert_timetable(cur, faculty_ids)
        lecture_count = insert_lectures(cur, timetable_rows)

        low_ids = [
            students_by_enrollment["LJIT55001"],
            students_by_enrollment["LJME33001"],
        ]
        high_ids = [
            students_by_enrollment["LJCE33001"],
            students_by_enrollment["LJIT33001"],
            students_by_enrollment["LJME77001"],
            students_by_enrollment["LJCE55001"],
            students_by_enrollment["LJIT77001"],
        ]

        attendance_count = insert_attendance(cur, low_ids, high_ids)
        enforce_thresholds(cur, low_ids, high_ids)

        conn.commit()

        print("Seed completed successfully.")
        print(f"Lectures inserted: {lecture_count}")
        print(f"Attendance rows inserted: {attendance_count}")
        for sid in low_ids:
            print(f"Student {sid} attendance %: {get_student_pct(cur, sid):.2f}")
        for sid in high_ids:
            print(f"Student {sid} attendance %: {get_student_pct(cur, sid):.2f}")

        cur.close()
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()

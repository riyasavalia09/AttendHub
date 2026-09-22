import mysql.connector

from config import Config


def get_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
    )


def table_exists(cur, table_name):
    cur.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = %s
        """,
        (table_name,),
    )
    return cur.fetchone()[0] > 0


def column_exists(cur, table_name, column_name):
    cur.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = %s
        """,
        (table_name, column_name),
    )
    return cur.fetchone()[0] > 0


def index_exists(cur, table_name, index_name):
    cur.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND index_name = %s
        """,
        (table_name, index_name),
    )
    return cur.fetchone()[0] > 0


def pick_lecture_table(cur):
    if table_exists(cur, "lecture"):
        return "lecture"
    if table_exists(cur, "lectures"):
        return "lectures"
    raise RuntimeError("Neither 'lecture' nor 'lectures' table exists")


def execute(cur, sql, params=None):
    cur.execute(sql, params or ())


def main():
    conn = get_connection()
    cur = conn.cursor()
    try:
        lecture_table = pick_lecture_table(cur)
        if not table_exists(cur, "timetable"):
            raise RuntimeError("Required table 'timetable' not found")

        print(f"Using lecture table: {lecture_table}")

        snapshot_columns = [
            ("subject_snapshot", "VARCHAR(150) NULL"),
            ("day_snapshot", "VARCHAR(16) NULL"),
            ("time_slot_snapshot", "VARCHAR(64) NULL"),
        ]

        for col_name, col_type in snapshot_columns:
            if not column_exists(cur, lecture_table, col_name):
                execute(
                    cur,
                    f"ALTER TABLE `{lecture_table}` ADD COLUMN `{col_name}` {col_type}",
                )
                print(f"Added column: {col_name}")

        if column_exists(cur, "timetable", "time_slot"):
            time_slot_expr = "t.`time_slot`"
        elif column_exists(cur, "timetable", "start_time") and column_exists(cur, "timetable", "end_time"):
            time_slot_expr = (
                "CONCAT(TIME_FORMAT(t.`start_time`, '%H:%i:%s'), ' - ', TIME_FORMAT(t.`end_time`, '%H:%i:%s'))"
            )
        else:
            time_slot_expr = "''"

        execute(
            cur,
            f"""
            UPDATE `{lecture_table}` l
            JOIN `timetable` t ON t.`timetable_id` = l.`timetable_id`
            SET
              l.`subject_snapshot` = COALESCE(l.`subject_snapshot`, t.`subject`),
              l.`day_snapshot` = COALESCE(l.`day_snapshot`, t.`day`),
              l.`time_slot_snapshot` = COALESCE(l.`time_slot_snapshot`, {time_slot_expr})
            WHERE
              l.`subject_snapshot` IS NULL
              OR l.`day_snapshot` IS NULL
              OR l.`time_slot_snapshot` IS NULL
            """
        )
        print("Backfilled snapshot columns")

        execute(
            cur,
            f"""
            UPDATE `{lecture_table}`
            SET
              `subject_snapshot` = COALESCE(`subject_snapshot`, ''),
              `day_snapshot` = COALESCE(`day_snapshot`, ''),
              `time_slot_snapshot` = COALESCE(`time_slot_snapshot`, '')
            """
        )

        execute(
            cur,
            f"""
            ALTER TABLE `{lecture_table}`
              MODIFY COLUMN `subject_snapshot` VARCHAR(150) NOT NULL,
              MODIFY COLUMN `day_snapshot` VARCHAR(16) NOT NULL,
              MODIFY COLUMN `time_slot_snapshot` VARCHAR(64) NOT NULL
            """
        )
        print("Set snapshot columns to NOT NULL")

        indexes = [
            ("idx_lecture_subject_snapshot", "(`subject_snapshot`)"),
            ("idx_lecture_day_snapshot", "(`day_snapshot`)"),
        ]

        if column_exists(cur, lecture_table, "lecture_date"):
            indexes.append(("idx_lecture_date_subject", "(`lecture_date`, `subject_snapshot`)"))

        for idx_name, idx_cols in indexes:
            if not index_exists(cur, lecture_table, idx_name):
                execute(
                    cur,
                    f"ALTER TABLE `{lecture_table}` ADD INDEX `{idx_name}` {idx_cols}",
                )
                print(f"Added index: {idx_name}")

        trigger_name = f"trg_{lecture_table}_snapshot_immutable_bu"
        execute(cur, f"DROP TRIGGER IF EXISTS `{trigger_name}`")
        execute(
            cur,
            f"""
            CREATE TRIGGER `{trigger_name}`
            BEFORE UPDATE ON `{lecture_table}`
            FOR EACH ROW
            BEGIN
              IF NEW.`subject_snapshot` <> OLD.`subject_snapshot`
                 OR NEW.`day_snapshot` <> OLD.`day_snapshot`
                 OR NEW.`time_slot_snapshot` <> OLD.`time_slot_snapshot`
              THEN
                SIGNAL SQLSTATE '45000'
                  SET MESSAGE_TEXT = 'Lecture snapshot columns are immutable';
              END IF;
            END
            """,
        )
        print(f"Created trigger: {trigger_name}")

        conn.commit()
        print("Migration completed successfully.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()

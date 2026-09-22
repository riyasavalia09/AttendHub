from db_connection import get_connection, close_connection
from exceptions.custom_exceptions import DatabaseError
from mysql.connector import Error


class PasswordResetRepository:
    """Repository for password reset token persistence."""

    @staticmethod
    def create_token(role: str, user_id: int, university_id: int, token_hash: str, expires_at):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO password_reset_tokens (role, user_id, university_id, token_hash, expires_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (role, user_id, university_id, token_hash, expires_at))
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            raise DatabaseError(f"Failed to create password reset token: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_valid_by_hash(token_hash: str):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT *
                FROM password_reset_tokens
                WHERE token_hash = %s
                  AND used_at IS NULL
                  AND expires_at > NOW()
                ORDER BY created_at DESC
                LIMIT 1
            """
            cursor.execute(query, (token_hash,))
            return cursor.fetchone()
        except Error as e:
            raise DatabaseError(f"Failed to find password reset token: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def mark_used(token_id: int):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE password_reset_tokens SET used_at = NOW() WHERE token_id = %s",
                (token_id,),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            raise DatabaseError(f"Failed to mark token used: {e}")
        finally:
            close_connection(conn)

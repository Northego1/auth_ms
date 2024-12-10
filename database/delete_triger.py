from database.db_setup import engine
from sqlalchemy import text

# Функция для создания функции триггера
async def create_delete_expired_tokens_function(conn):
    query = """
    CREATE OR REPLACE FUNCTION delete_expired_tokens()
    RETURNS TRIGGER AS $$
    BEGIN
        DELETE FROM black_list_access_jwt
        WHERE expiration_time < NOW();
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """
    await conn.execute(text(query))

# Функция для создания триггера
async def create_remove_expired_tokens_trigger(conn):
    query = """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_delete_expired_tokens'
        ) THEN
            CREATE TRIGGER trigger_delete_expired_tokens
            AFTER INSERT OR UPDATE ON black_list_access_jwt
            FOR EACH ROW
            EXECUTE FUNCTION delete_expired_tokens();
        END IF;
    END;
    $$;
    """
    await conn.execute(text(query))

# Основная функция для запуска триггера
async def start_triggers() -> None:
    async with engine.connect() as conn:
        await create_delete_expired_tokens_function(conn)
        await create_remove_expired_tokens_trigger(conn)

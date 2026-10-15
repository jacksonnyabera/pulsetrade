from app.core.config import settings
import psycopg2
u = settings.database_url.replace("+asyncpg", "")
print("host:", u.split("@")[-1].split("/")[0])
c = psycopg2.connect(u)
cur = c.cursor()
cur.execute("select table_name from information_schema.tables where table_schema='public' order by 1")
print([r[0] for r in cur.fetchall()])

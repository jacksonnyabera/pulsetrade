[33mcommit 21ada8d9b56392f40efe7882c13e9f9efb1c2bf3[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m)[m
Author: Jackson Nyabera <maobe928@gmail.com>
Date:   Wed Sep 23 23:38:23 2026 +0300

    Fix: actually register the market router

[1mdiff --git a/backend/app/main.py b/backend/app/main.py[m
[1mindex 6abc26f..78be01f 100644[m
[1m--- a/backend/app/main.py[m
[1m+++ b/backend/app/main.py[m
[36m@@ -20,7 +20,7 @@[m [mapp.add_middleware([m
 [m
 app.include_router(auth_router, prefix="/api/v1")[m
 app.include_router(deriv_router, prefix="/api/v1")[m
[31m-[m
[32m+[m[32mapp.include_router(market_router, prefix="/api/v1")[m
 [m
 @app.get("/health")[m
 async def health_check():[m
[1mdiff --git a/docker/volumes/postgres/global/pg_control b/docker/volumes/postgres/global/pg_control[m
[1mindex 916e5db..2c7be72 100644[m
Binary files a/docker/volumes/postgres/global/pg_control and b/docker/volumes/postgres/global/pg_control differ
[1mdiff --git a/docker/volumes/postgres/pg_wal/000000010000000000000001 b/docker/volumes/postgres/pg_wal/000000010000000000000001[m
[1mindex be374a5..0ac0b4e 100644[m
Binary files a/docker/volumes/postgres/pg_wal/000000010000000000000001 and b/docker/volumes/postgres/pg_wal/000000010000000000000001 differ
[1mdiff --git a/docker/volumes/postgres/postmaster.pid b/docker/volumes/postgres/postmaster.pid[m
[1mindex 3666cfc..84962e3 100644[m
[1m--- a/docker/volumes/postgres/postmaster.pid[m
[1m+++ b/docker/volumes/postgres/postmaster.pid[m
[36m@@ -1,6 +1,6 @@[m
 1[m
 /var/lib/postgresql/data[m
[31m-1790122933[m
[32m+[m[32m1790187703[m
 5432[m
 /var/run/postgresql[m
 *[m

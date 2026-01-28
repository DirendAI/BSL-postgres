"""Check that basic features work.

Catch cases where e.g. files are missing so the import doesn't work. It is
recommended to check that e.g. assets are included."""

from bsl_psql.server import BSLPostgresServer

server = BSLPostgresServer("localhost", 5050)
if isinstance(server, BSLPostgresServer):
    print("Smoke test succeeded")
else:
    raise RuntimeError("Smoke test failed")
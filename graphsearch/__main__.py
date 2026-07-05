"""Allow ``python -m graphsearch`` to start the server.

This always works, even when pip's Scripts directory (where the
``graphsearch`` console command lives) is not on PATH — common with
``pip install --user`` on Windows.
"""

from .main import run

if __name__ == "__main__":
    run()

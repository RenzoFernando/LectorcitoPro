import os
import sys

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app_controller import AppController  # noqa: E402


def main():
    app = AppController()
    app.run()


if __name__ == "__main__":
    main()

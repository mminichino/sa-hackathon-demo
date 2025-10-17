import sys
import os
from dotenv import load_dotenv
from streamlit.web import cli as stcli

current = os.path.dirname(os.path.realpath(__file__))


def main():
    load_dotenv()
    sys.argv = ["streamlit", "run", f"{current}/ui.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
    sys.exit(stcli.main())


if __name__ == '__main__':
    main()

import os


def run_site():
    os.system("streamlit run streamlit_dash_2.py --server.port 8502")


if __name__ == '__main__':
    print("STARTED!")
    run_site()
    while True:
        pass

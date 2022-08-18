import subprocess
import os


def run_site():
    # cmd_line = ['streamlit', 'run', 'streamlit_dash', '--server.port', '8502']
    # p = subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # p.communicate()

    os.system("streamlit run streamlit_dash.py")


if __name__ == '__main__':
    print("STARTED!")
    run_site()
    while True:
        pass

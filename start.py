import subprocess


def run_site():
    cmd_line = ['streamlit', 'run', 'streamlit_dash.py', '--server.port', '8501', '--server.address', '10.87.181.67']
    p = subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.communicate()


if __name__ == '__main__':
    print("STARTED!")
    count = 1
    run_site()
    while count == 1:
        pass

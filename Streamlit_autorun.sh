# !/bin/bash

SESSIONNAME="StreamlitSession"
SESSIONNAME_2="StreamlitSession_2"
# Флаг -d сообщает tmux о том, что ему не нужно входить в новую сессию, подключаться к ней

tmux kill-server
tmux new-session -d -s $SESSIONNAME
tmux send-keys -t $SESSIONNAME "cd /home/Access/CP_Exploitation/Scripts/Streamlit" Enter
tmux send-keys -t $SESSIONNAME "python3.9 start.py" Enter

tmux new-session -d -s $SESSIONNAME_2
tmux send-keys -t $SESSIONNAME_2 "cd /home/Access/CP_Exploitation/Scripts/Streamlit" Enter
tmux send-keys -t $SESSIONNAME_2 "python3.9 start_2.py" Enter

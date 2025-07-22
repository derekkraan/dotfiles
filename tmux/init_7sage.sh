#!/bin/bash

set -euC

SESSION="7Sage2"

att() {
  [ -n "${TMUX:-}" ] &&
    tmux switch-client -t $SESSION ||
    tmux attach-session -t $SESSION
}

if tmux has-session -t $SESSION 2> /dev/null; then
  att
  exit 0
fi

tmux new-session -d -s $SESSION
tmux rename-window -t "$SESSION:0" "code"
tmux send-keys -t "$SESSION:code" "zsh" C-m "cd ~/Code/7sage/phoenix" C-m "clear" C-m "vim" C-m
tmux split-window -t "$SESSION:code" -h -p 50
tmux send-keys -t "$SESSION:code" "cd ~/Code/7sage/phoenix" C-m "clear" C-m

tmux new-window -t $SESSION:1 -n "phx_server"
tmux send-keys -t "$SESSION:phx_server" "cd ~/Code/7sage/phoenix" C-m "clear" C-m "just" C-m

tmux new-window -t $SESSION:2 -n "port_fw"
tmux send-keys -t "$SESSION:port_fw" "cd ~/Code/7sage/phoenix" C-m "clear" C-m "just port-forward" C-m

tmux new-window -t $SESSION:2 -n "lazygit"
tmux send-keys -t "$SESSION:lazygit" "cd ~/Code/7sage/phoenix" C-m "clear" C-m "lazygit" C-m

att

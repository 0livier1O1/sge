#!/bin/bash

# Check if both arguments are provided
if [ $# -lt 2 ]
then
    echo "Please provide number of agents and base path as arguments"
    echo "Usage: ./start_agents.sh <number_of_agents> <base_path>"
    exit 1
fi

# Get arguments
N_AGENTS=$1
BASE=$2

# Create required directories
mkdir -p "${BASE}log"
mkdir -p "${BASE}agent_pool"
mkdir -p "${BASE}job_pool"
mkdir -p "${BASE}result_pool"
mkdir -p "${BASE}data"

# Add current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Loop to create N tmux sessions (0 to N-1)
for i in $(seq 0 $(($N_AGENTS-1)))
do
    tmux new-session -s sge_$i -d "python -m sge.gpu_session $i $BASE"
    echo "Started agent $i in tmux session sge_$i"
done

# Show running tmux sessions
echo "Running tmux sessions:"
tmux ls
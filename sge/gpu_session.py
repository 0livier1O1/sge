import time, sys, os, logging
import numpy as np
from pathlib import Path
from expensive_task import expensive_task

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

# First set up the workstation
agent_id = int(sys.argv[1])
BASE = sys.argv[2]

# Set up a log
log_name = BASE + '/log/{}.log'.format(agent_id)
logging.basicConfig(
	filename=log_name, filemode='a', level=logging.DEBUG, format='%(asctime)s: %(message)s', datefmt='%H:%M:%S')

# Set up console output
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s:  %(message)s'))  # same format as logging
logging.getLogger('').addHandler(console)
	

def check_and_load(agent_id):
    # Get agent's POOL file path
    file_name = BASE + 'agent_pool/{}.POOL'.format(agent_id)
    
    # Return False if file empty
    if os.stat(file_name).st_size == 0:
        return False, False
        
    # Load and return goal data if file not empty
    with open(file_name, 'r') as f:
        shared_data_loc = f.readline()
        shared_data = np.load(shared_data_loc)
    return True, shared_data


if __name__=="__main__":
    # Start unit (agent)
    Path(BASE + '/agent_pool/{}.POOL'.format(agent_id)).touch()  

    while True:
        # TODO Lock GPU
        flag, shared_data = check_and_load(agent_id)  # Check if any job is waiting
        
        if flag:
            job = np.load(BASE + '/job_pool/{}.npz'.format(agent_id), allow_pickle=True)

            A, B = job['matrix_a'], job['matrix_b']
            name = job['name']
            logging.info(f'Receiving job {name}...')

            try:
                result, is_cuda = expensive_task(
                    A=A,
                    B=B,
                    shared_data=shared_data, 
                    gpu_id=agent_id
                )
                
                # Just logging
                logging.info(f'Agent {agent_id} completed task - (GPU:{is_cuda}).')
                np.savez(
                    BASE + f'/result_pool/{name}.npz',
                    matrix_a=A,
                    name=name,
                    matrix_b=B,
                    result=result
                )

                os.remove(BASE + '/job_pool/{}.npz'.format(agent_id))
                open(BASE + '/agent_pool/{}.POOL'.format(agent_id), 'w').close()

            except Exception as e:
                os.remove(BASE + '/agent_pool/{}.POOL'.format(agent_id))
                raise e
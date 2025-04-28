from sge.master import Master
from sge.jobs import Job

import os, logging

BASE = './sge/comms/'  # Where to keep file system
GPU_COUNT = 2   
HOT_START = False  # Set to False if you want to start agents from scratch, True if you want to customized sessions 


if __name__ == '__main__':

    comms_system = ["log", "agent_pool", "job_pool", "result_pool", "data"]
    # Start agents
    if not HOT_START:
        os.system(f"./start_agents.sh {GPU_COUNT} {BASE}")  # DO NOT RUN IF 
    else:
        for folder in comms_system:
            if not os.path.exists(BASE + folder):
                raise ValueError(f"Folder {BASE + folder} does not exist. Please check the BASE path and try again.")
        
    # Some logging 
    log_name = BASE + 'log/sge_example.log'

    # Create logger
    logger = logging.getLogger('sge')
    logger.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler(log_name)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S'))
    logger.addHandler(file_handler)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(asctime)s:  %(message)s'))
    logger.addHandler(console)


    import numpy as np
    
    # Create large tensors for testing GPU memory and computation
    n_tasks = 10
    dim1, dim2 = 5000, 10000
    m = 5000

    tasks = []
    for i in range(n_tasks):
        data = {
            'matrix_a': np.random.randn(dim1, m), 
            'matrix_b': np.random.randn(m, dim2),
        }
        tasks.append(Job(name=f'job_{i}', data=data))
    
    # Create shared matrix that will be used by all tasks
    matrix_c = np.random.randn(m, m)
    np.savez(BASE + "data/shared.npz", matrix_c=matrix_c)

    # TODO: Shared data is needed (even an empty matrix) to let agents properly display status to master (need to fix)
    pipeline = Master(
        base_path=BASE, 
        shared_data_path=BASE + "data/shared.npz",
        logger=logger)
    
    pipeline.run(tasks)

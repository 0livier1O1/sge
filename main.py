from sge.master import Master
from sge.jobs import Job

import os, logging, sys

BASE = './sge/comms/'
gpus = 2    


if __name__ == '__main__':

    # Start agents
    os.system(f"./start_agents.sh {gpus} {BASE}")

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

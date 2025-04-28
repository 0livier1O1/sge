import torch, time

def expensive_task(A, B, gpu_id, cpu=False, **kwargs):
    shared_data = kwargs['shared_data']
    
    device = torch.device(f'cuda:{gpu_id}' if not cpu else 'cpu')

    A = torch.tensor(A).to(device=device)
    B = torch.tensor(B).to(device=device)
    
    M = torch.tensor(shared_data["matrix_c"]).to(device=device)
    
    O = torch.zeros(A.shape[0], B.shape[1]).to(device=device)

    for i in range(10):
        O += (A @ M) @ B
        
    # time.sleep(5)
    return O.norm().cpu().numpy(), device.type=='cuda'



if __name__ == "__main__":
    # Example use
    m = 1000
    K = 50000

    data = {
        'matrix_a': torch.randn(K, m),
        'matrix_b': torch.randn(m, K),
    }

    shared_data = {"matrix_c": torch.randn(m, m)}
    
    start = time.time()
    expensive_task(gpu_id=0, A=data["matrix_a"], B=data["matrix_b"], shared_data=shared_data, 
                       cpu=False)
    end = time.time()
    print(f"Time taken on GPU: {end - start:.2f} seconds")

    start = time.time()
    expensive_task(gpu_id=0, A=data["matrix_a"], B=data["matrix_b"], shared_data=shared_data, 
                       cpu=True)
    end = time.time()
    print(f"Time taken on CPU: {end - start:.2f} seconds")


    
import random
import warnings
import numpy as np
import torch
from tqdm import tqdm

warnings.filterwarnings(
    'ignore',
    message='dtype\\(\\): align should be passed as Python or NumPy boolean',
    category=np.VisibleDeprecationWarning,
)

from servers import Server
from validators import ValidatorClassification, ValidatorConfig
from models import Cifar10CnnModel
from solvers import ServerSolver, Cifar10CNNClientSolver
from utils import init_exp, logger
from clients_preparation import create_clients_cifar_and_cifar_rotation_90


SEEDS = [0, 1, 2, 3, 4]
GPU_MEMORY_FRACTION = 0.5  # 使用するVRAMの割合 (0.0〜1.0)


def set_gpu_memory_limit(fraction: float):
    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(fraction)
        total_mb = torch.cuda.get_device_properties(0).total_memory / 1024 ** 2
        tqdm.write(f'[GPU] Memory limit: {fraction * 100:.0f}% of {total_mb:.0f} MB '
                   f'= {total_mb * fraction:.0f} MB')


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def run_experiment(exp_id: str, seed: int):
    set_seed(seed)

    num_epochs = 200
    model_fn = Cifar10CnnModel
    server_solver = ServerSolver(
        estimation_interval=2,
        do_selection=True,
        selection_size=15,
    )
    client_solver = Cifar10CNNClientSolver()
    client_vec, test_ds_vec, preparation_dict = create_clients_cifar_and_cifar_rotation_90(client_solver)
    validator_config = ValidatorConfig(
        num_class=preparation_dict['num_classes'],
        num_epochs=num_epochs,
        do_cluster_eval=True,
        do_client_eval=True,
        do_importance_estimation=True,
        client_eval_idx_vec=range(preparation_dict['num_clients']),
    )

    logger.log_server_solver(exp_id, server_solver.to_json_dict())
    logger.log_client_solver(exp_id, client_solver.to_json_dict())
    logger.log_client_preparation(exp_id, preparation_dict)
    logger.log_model_description(exp_id, model_fn)

    server = Server(
        model_fn=model_fn,
        client_vec=client_vec,
        num_clusters=preparation_dict['num_clusters'],
        server_solver=server_solver,
        validator=ValidatorClassification(test_ds_vec, validator_config),
        exp_id=exp_id,
    )
    server.run(num_global_epochs=num_epochs)


def main():
    set_gpu_memory_limit(GPU_MEMORY_FRACTION)
    for seed in tqdm(SEEDS, desc='Experiments', unit='exp'):
        exp_id = f'cifar10_seed{seed}'
        tqdm.write(f'\n[Experiment] seed={seed}  exp_id={exp_id}')

        init_exp(exp_id)
        logger.log_exp_info(
            exp_id,
            description=f'CIFAR-10 FedSoft experiment with seed={seed}',
        )
        run_experiment(exp_id, seed)

    tqdm.write('\nAll experiments completed.')


if __name__ == '__main__':
    main()

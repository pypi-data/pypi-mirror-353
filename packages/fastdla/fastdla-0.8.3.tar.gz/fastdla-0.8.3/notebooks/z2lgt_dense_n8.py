import os
import logging
import numpy as np
import h5py
import jax
import jax.numpy as jnp
from jax.experimental.sparse import bcsr_dot_general
from fastdla.lie_closure import lie_closure
from fastdla.generators.z2lgt_hva import z2lgt_hva_generators, z2lgt_symmetry_eigenspace

os.environ['CUDA_VISIBLE_DEVICES'] = '6'
os.environ['XLA_PYTHON_CLIENT_MEM_FRACTION'] = '.99'
jax.config.update('jax_enable_x64', True)

logging.basicConfig(level=logging.WARNING)
logging.getLogger('fastdla').setLevel(logging.INFO)

data_file = '/data/iiyama/z2lgt_hva_dla_jun05.h5'

num_fermions = 4
# Determine the charge sector (symmetry subspace) to investigate
gauss_eigvals = [1, -1, 1, -1, 1, -1, 1, -1]
u1_total_charge = 0
t_jphase = 0

generators_full = z2lgt_hva_generators(num_fermions).to_matrices(sparse=True, npmod=jnp)
symm_eigenspace = z2lgt_symmetry_eigenspace(gauss_eigvals, u1_total_charge, t_jphase, npmod=jnp)
generators_reduced = []
for gen in generators_full:
    projected = bcsr_dot_general(gen, symm_eigenspace, dimension_numbers=(([1], [0]), ([], [])))
    generators_reduced.append(symm_eigenspace.conjugate().T @ projected)
generators_reduced = jnp.array(generators_reduced)

max_dim = generators_reduced.shape[-1] ** 2 - 1

# Compute the DLA of the subspace
dla_dimonly = lie_closure(generators_reduced)
print(f'Subspace DLA dimension is {len(dla_dimonly)}')

with h5py.File(data_file, 'a') as out:
    if 'nf=4' not in out:
        nf_group = out.create_group('nf=4')
        for gname, oplist in [
            ('generators', generators_reduced)
        ]:
            group = nf_group.create_group(gname)
            group.create_dataset('ops', data=np.array(oplist))

        nf_group.create_group('dla_symm0')
        nf_group.create_dataset('dla_symm0/dim', data=dla_dimonly)
        nf_group.create_dataset('dla_symm0/gauss_eigvals', data=gauss_eigvals)
        nf_group.create_dataset('dla_symm0/charge', data=u1_total_charge)
        nf_group.create_dataset('dla_symm0/t_jphase', data=t_jphase)

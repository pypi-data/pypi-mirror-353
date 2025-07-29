def z2lgt_dense_charge_projector(
    projector: np.ndarray,
    c_eigval: int,
    npmod=np
) -> np.ndarray:
    """Project out the subspace spanned by states with specific C eigenvalues from the projector.

    Charge conjugation is defined as a reflection about sites 0-1 followed by X on all sites.

    Since C does not commute with G_n and Q, we simply rely on linear algebra. Let P† represent
    the given projector array (shape (p, 2**nq)). A vector in the space spanned by columns of P is
    given by Pα, where α is a column vector with p entries. When this vector is an eigenvector of
    C,
        C Pα = c Pα ⇒ (C - cI)Pα = 0
    If the SVD of (C - cI)P is UΣV†, α is the conjugate of a row of V† corresponding to a zero
    singular value. We identify such αs and return the reduced projector [P (α0 α1 ...)]†.
    """
    if c_eigval not in [1, -1]:
        raise ValueError('Invalid C eigenvalue')

    num_qubits = np.round(np.log2(projector.shape[1])).astype(int)
    num_sites = num_qubits // 2

    pmat = projector.conjugate().T

    pdim = projector.shape[0]
    conjugate = pmat.reshape((2,) * num_qubits + (pdim,))
    swap = npmod.array([[1., 0., 0., 0.], [0., 0., 1., 0.], [0., 1., 0., 0.], [0., 0., 0., 1.]])
    swap = swap.reshape((2,) * 4)
    paulix = npmod.array([[0., 1.], [1., 0.]])
    for iqubit in range(2, num_sites + 1):
        # Swap qubit i and 2 - i
        iax_src = num_qubits - iqubit - 1
        iax_dest = num_qubits - ((2 - iqubit) % num_qubits) - 1
        conjugate = npmod.moveaxis(
            npmod.tensordot(swap, conjugate, [[2, 3], [iax_src, iax_dest]]),
            [0, 1], [iax_src, iax_dest]
        )

    # Apply the X gate to each site
    for isite in range(num_sites):
        iax = num_qubits - isite * 2 - 1
        conjugate = npmod.moveaxis(
            npmod.tensordot(paulix, conjugate, [[1], [iax]]),
            0, iax
        )

    conjugate = conjugate.reshape((2 ** num_qubits, pdim))
    _, svals, vhmat = npmod.linalg.svd(conjugate - c_eigval * pmat, full_matrices=False)
    indices = npmod.nonzero(npmod.isclose(svals, 0.))[0]
    subspace = vhmat[indices]

    projector = subspace @ projector

    return projector

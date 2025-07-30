from typing import Optional

from ngsolve import (
    BND,
    COUPLING_TYPE,
    L2,
    CoefficientFunction,
    InnerProduct,
    Mesh,
    NormalFacetFESpace,
    VectorL2,
    div,
    dx,
    grad,
    specialcf,
)
from ngstrefftz import (
    CompoundEmbTrefftzFESpace,
    EmbeddedTrefftzFES,
    TrefftzEmbedding,
)

from ngstSpaceKit.diffops import laplace


def WeakStokes(
    mesh: Mesh,
    order: int,
    normal_continuity: Optional[int] = None,
    rhs: Optional[CoefficientFunction] = None,
    nu: float = 1.0,
    dirichlet: str = "",
) -> CompoundEmbTrefftzFESpace:
    r"""
    The weak Stokes space
    - is taylored to be used to solve the Stokes equation
    - is normal continuous up to degree `normal_continuity` in the velocity part
    - has the remaining dofs adhering to the embedded Trefftz condition:

      For $u \in V_h^k, p \in V_h^{k-1}$, for all $v \in V^{k-2}, q \in V^{k-1}_{h,0}$ holds
      $$
      -\nu \int_\Omega \Delta u \cdot v \;\mathrm{d}x + \int_\Omega \nabla p \cdot v + \mathrm{div}(u) q \;\mathrm{d}x = 0.
      $$

    `normal_continuity`: If `None`, it is set to `order-1`.
    """
    if order < 2:
        raise ValueError("requires order>=2")

    fes = VectorL2(mesh, order=order, dgjumps=True) * L2(
        mesh, order=order - 1, dgjumps=True
    )

    Q_test = L2(mesh, order=order - 1, dgjumps=True)
    for i in range(0, Q_test.ndof, Q_test.ndof // mesh.ne):
        Q_test.SetCouplingType(i, COUPLING_TYPE.UNUSED_DOF)

    fes_test = VectorL2(mesh, order=order - 2, dgjumps=True) * Q_test

    (u, p) = fes.TrialFunction()
    (v, q) = fes_test.TestFunction()

    top = (
        -nu * InnerProduct(laplace(u), v) * dx
        + InnerProduct(grad(p), v) * dx
        + div(u) * q * dx
    )
    trhs = rhs * v * dx(bonus_intorder=10) if rhs else None

    conformity_space = NormalFacetFESpace(
        mesh,
        order=normal_continuity if normal_continuity is not None else order - 1,
        dirichlet=dirichlet,
    )

    uc, vc = conformity_space.TnT()

    n = specialcf.normal(mesh.dim)

    cop_l = u * n * vc * n * dx(element_vb=BND)
    cop_r = uc * n * vc * n * dx(element_vb=BND)

    emb = TrefftzEmbedding(top=top, trhs=trhs, cop=cop_l, crhs=cop_r)
    weak_stokes = EmbeddedTrefftzFES(emb)
    assert type(weak_stokes) is CompoundEmbTrefftzFESpace, (
        "The weak Stokes space should always be an CompoundEmbTrefftzFESpace"
    )

    return weak_stokes

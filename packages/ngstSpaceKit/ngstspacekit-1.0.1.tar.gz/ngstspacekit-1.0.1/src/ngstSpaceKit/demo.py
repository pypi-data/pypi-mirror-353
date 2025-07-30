"""
Spaces in `ngstSpaceKit.demo` are already natively implemented in NGSolve.
Their implementation here is purely for educational purposeses.
"""

import ngsolve
from ngsolve import (
    BND,
    L2,
    TET,
    TRIG,
    Discontinuous,
    FacetFESpace,
    HCurl,
    NormalFacetFESpace,
    VectorL2,
    dx,
    specialcf,
)
from ngstrefftz import (
    EmbeddedTrefftzFES,
    L2EmbTrefftzFESpace,
    TrefftzEmbedding,
    VectorL2EmbTrefftzFESpace,
)

import ngstSpaceKit
from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)


def CrouzeixRaviart(
    mesh: ngsolve.comp.Mesh, dirichlet: str = ""
) -> L2EmbTrefftzFESpace:
    """
    This is an implementation of the Crouzeix-Raviart element via an embedded Trefftz FESpace.
    This implementation is done for illustrative purposes,
    as ngsolve already implements the Crouzeix-Raviart element with:
    ```python
    fes_cr = FESpace('nonconforming', mesh)
    ```

    # Raises
    - ValueError, if the mesh is not 2D
    - ValueError, if the mesh is not triangular
    """
    throw_on_wrong_mesh_dimension(mesh, 2)
    throw_on_wrong_mesh_eltype(mesh, TRIG)

    fes = L2(mesh, order=1)
    conformity_space = FacetFESpace(mesh, order=0, dirichlet=dirichlet)

    u = fes.TrialFunction()

    uc, vc = conformity_space.TnT()

    cop_l = u * vc * dx(element_vb=BND)
    cop_r = uc * vc * dx(element_vb=BND)

    embedding = TrefftzEmbedding(cop=cop_l, crhs=cop_r)

    cr = EmbeddedTrefftzFES(embedding)
    assert type(cr) is L2EmbTrefftzFESpace, (
        "The cr space should always be an L2EmbTrefftzFESpace"
    )
    return cr


def H1(
    mesh: ngsolve.comp.Mesh, order: int, dirichlet: str = ""
) -> L2EmbTrefftzFESpace:
    """
    This is an implementation for illustrative purposes, ngsolve already implements the H1 space.
    The H1 space is implemented via an embedded Trefftz FESpace.
    Note, that the conformity space is the ngsolve.H1 space,
    which is only used for point evaluations the the mesh vertices.
    """
    fes = L2(mesh, order=order)
    cfes = ngsolve.H1(mesh, order=order, dirichlet=dirichlet)

    u, v = fes.TnT()
    uc, vc = cfes.TnT()

    # cop_l = u * vc * dx(element_vb=BBND)
    # cop_r = uc * vc * dx(element_vb=BBND)
    cop_l = u * vc * dx()
    cop_r = uc * vc * dx()

    embedding = TrefftzEmbedding(cop=cop_l, crhs=cop_r, ndof_trefftz=0)

    h1 = EmbeddedTrefftzFES(embedding)
    assert type(h1) is L2EmbTrefftzFESpace, (
        "The h1 space should always be an L2EmbTrefftzFESpace"
    )

    return h1


def BDM(
    mesh: ngsolve.comp.Mesh, order: int, dirichlet: str = ""
) -> VectorL2EmbTrefftzFESpace:
    """
    This BDM space is tailored to mimic the ngsolve implementation of the BDM space:
    ```python
        fes_bdm = HDiv(mesh, order=order, RT=False)
    ```
    Therefore, this implementation has no practical advantage over the ngsolve implementation,
    and merely serves as a demonstration.

    See `ngstSpaceKit.HDiv` for an H(div) conforming space, that is not implemented by ngsolve.

    # Raises
    - ValueError, if `order == 0`
    - ValueError, if the mesh is not 2D or 3D
    - ValueError, if the mesh is not triangular (2D) or consists of tetrahedra (3D)
    """

    throw_on_wrong_mesh_dimension(mesh, [2, 3])
    throw_on_wrong_mesh_eltype(mesh, [TRIG, TET])

    if order == 0:
        raise ValueError("BDM needs order >= 1")
    if order == 1:
        return ngstSpaceKit.HDiv(mesh, order=1)

    fes = VectorL2(mesh, order=order)

    conformity_space = NormalFacetFESpace(
        mesh, order=order, dirichlet=dirichlet
    ) * Discontinuous(
        HCurl(mesh, order=order - 1, type1=True, dirichlet=dirichlet)
    )

    u = fes.TrialFunction()

    (uc_edge, uc_vol), (vc_edge, vc_vol) = conformity_space.TnT()

    n = specialcf.normal(mesh.dim)

    cop_l = u * n * vc_edge * n * dx(element_vb=BND)
    cop_r = uc_edge * n * vc_edge * n * dx(element_vb=BND)

    cop_l += u * vc_vol * dx
    cop_r += uc_vol * vc_vol * dx

    embedding = TrefftzEmbedding(cop=cop_l, crhs=cop_r)

    bdm = EmbeddedTrefftzFES(embedding)
    assert type(bdm) is VectorL2EmbTrefftzFESpace, (
        "The bdm space should always be a VectorL2EmbTrefftzFESpace"
    )

    return bdm

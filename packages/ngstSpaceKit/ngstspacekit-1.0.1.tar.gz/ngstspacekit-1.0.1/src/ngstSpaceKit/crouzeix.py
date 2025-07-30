import ngsolve
from ngsolve import (
    BND,
    L2,
    TRIG,
    FacetFESpace,
    dx,
)
from ngstrefftz import EmbeddedTrefftzFES, L2EmbTrefftzFESpace, TrefftzEmbedding

from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)


def CrouzeixFalk(
    mesh: ngsolve.comp.Mesh, dirichlet: str = ""
) -> L2EmbTrefftzFESpace:
    """
    Crouzeix - Falk FE Space (through an Embedded Trefftz FESpace).

    This FESpace is the Embedded Trefftz FESpace for the Crouzeix Falk element.
    The element is a triangle with 3 edge dofs per edge and 1 element midpoint dof.
    This implementation does not take nodal values at Gauss points as dofs (as in the
    original paper), but instead uses the P2 modes on facets. The resulting space is
    the same, i.e. the space of cubic polynomials with "relaxed H1-conformity", i.e.
    jumps across facets that are zero after L2-projection into P2. This implies
    continuity across the three Gauss points on each facet.

    For further information, see `CrouzeixHO`.
    """

    return CrouzeixHO(mesh, 3, dirichlet)


def CrouzeixHO(
    mesh: ngsolve.comp.Mesh, order: int, dirichlet: str = ""
) -> L2EmbTrefftzFESpace:
    """

    Higher Order Crouzeix(-Raviart) FE Space (through an Embedded Trefftz FESpace).
    This is a "relaxed H1-conformity" space with continuity up to degree k-2.

    `order`: odd and positive integer

    `dirichlet`: expression for dirichlet dofs

    # raises
    - ValueError, if order is even
    - ValueError, if the mesh is not 2D
    - ValueError, if the mesh is not triangular
    """
    if order % 2 == 0:
        raise ValueError(f"order {order} is even, but it needs to be odd.")
    throw_on_wrong_mesh_dimension(mesh, 2)
    throw_on_wrong_mesh_eltype(mesh, TRIG)

    fes = L2(mesh, order=order)

    # the first space holds k edge dofs,
    # the second space is for the (k-1)(k-2)/2 element midpoint dofs
    conformity_space = FacetFESpace(
        mesh, order=order - 1, dirichlet=dirichlet
    ) * L2(mesh, order=max(order - 3, 0))

    u = fes.TrialFunction()

    uc, vc = conformity_space.TnT()

    cop_l = u * vc[1] * dx
    cop_r = uc[1] * vc[1] * dx

    cop_l += u * vc[0] * dx(element_vb=BND)
    cop_r += uc[0] * vc[0] * dx(element_vb=BND)

    embedding = TrefftzEmbedding(cop=cop_l, crhs=cop_r, ndof_trefftz=0)

    crho = EmbeddedTrefftzFES(embedding)
    assert type(crho) is L2EmbTrefftzFESpace, (
        "The higher order crouzeix space should always be an L2EmbTrefftzFESpace"
    )

    return crho

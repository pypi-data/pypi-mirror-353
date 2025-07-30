from dataclasses import dataclass

import ngsolve
from ngsolve import (
    BBND,
    H1,
    L2,
    QUAD,
    dx,
)
from ngstrefftz import EmbeddedTrefftzFES, L2EmbTrefftzFESpace, TrefftzEmbedding

from ngstSpaceKit.diffops import del_x, del_xy, del_y
from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)


@dataclass
class BFSDirichlet:
    """
    Holds the dirichlet instructions for every type of dof in the `BFS` space separately.
    """

    vertex_value: str = ""
    deriv_x: str = ""
    deriv_y: str = ""
    deriv_xy: str = ""

    @classmethod
    def clamp_weak(cls, bnd: str) -> "BFSDirichlet":
        """
        `bnd`: boundary where (weak) clamp conditions shall be set.

        By the nature of the `BFS` space, the clamp conditions will not apply to the whole boundary,
        but only at certain points along the boundary. Further action is necessary to completely enforce clamp conditions.
        """
        return cls(vertex_value=bnd, deriv_x=bnd, deriv_y=bnd)


def BognerFoxSchmitt(
    mesh: ngsolve.comp.Mesh, dirichlet: str | BFSDirichlet = ""
) -> L2EmbTrefftzFESpace:
    """
    This element is for quads.

    `dirichlet`: if you provide a string, it will set dirichlet conditions only for vertex value dofs. For more control, use `BFSDirichlet`.

    # Raises
    - ValueError, if the mesh is not 2D
    - ValueError, if the mesh is not rectangular
    """
    throw_on_wrong_mesh_dimension(mesh, 2)
    throw_on_wrong_mesh_eltype(mesh, QUAD)

    dirichlet_struct = (
        BFSDirichlet(vertex_value=dirichlet)
        if type(dirichlet) is str
        else dirichlet
    )
    assert type(dirichlet_struct) is BFSDirichlet

    fes = L2(mesh, order=3)
    vertex_value_space = H1(
        mesh, order=1, dirichlet=dirichlet_struct.vertex_value
    )
    deriv_x_value_space = H1(mesh, order=1, dirichlet=dirichlet_struct.deriv_x)
    deriv_y_value_space = H1(mesh, order=1, dirichlet=dirichlet_struct.deriv_y)
    deriv_xy_value_space = H1(
        mesh, order=1, dirichlet=dirichlet_struct.deriv_xy
    )

    conformity_space = (
        vertex_value_space
        * deriv_x_value_space
        * deriv_y_value_space
        * deriv_xy_value_space
    )

    u = fes.TrialFunction()
    (u_, u_dx, u_dy, u_dxy) = conformity_space.TrialFunction()
    (v_, v_dx, v_dy, v_dxy) = conformity_space.TestFunction()

    dVertex = dx(element_vb=BBND)

    cop_lhs = (
        u * v_ * dVertex
        + del_x(u) * v_dx * dVertex
        + del_y(u) * v_dy * dVertex
        + del_xy(u) * v_dxy * dVertex
    )
    cop_rhs = (
        u_ * v_ * dVertex
        + u_dx * v_dx * dVertex
        + u_dy * v_dy * dVertex
        + u_dxy * v_dxy * dVertex
    )

    embedding = TrefftzEmbedding(cop=cop_lhs, crhs=cop_rhs, ndof_trefftz=0)

    bfs = EmbeddedTrefftzFES(embedding)
    assert type(bfs) is L2EmbTrefftzFESpace, (
        "The bfs space should always be an L2EmbTrefftzFESpace"
    )

    return bfs

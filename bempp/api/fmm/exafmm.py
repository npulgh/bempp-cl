"""Interface to ExaFMM."""
from .common import FmmInterface
import numpy as _np


class ExafmmLaplace(FmmInterface):
    """Interface to ExaFmm."""

    def __init__(self):
        """Initalize the ExaFmm Interface."""
        self._domain = None
        self._dual_to_range = None
        self._regular_order = None
        self._singular_order = None
        self._sources = None
        self._targets = None

        self._source_transform = None
        self._target_transform = None

        self._local_points = None

        self._nodes = {}
        self._leaf_nodes = []

        self._near_field_matrix = None

    def setup(
        self,
        domain,
        dual_to_range,
        regular_order,
        singular_order,
        expansion_order=10,
        ncritical=100,
        max_level=-1,
    ):
        """Setup the Fmm computation."""
        from bempp.api.integration.triangle_gauss import rule
        import exafmm_laplace

        self._domain = domain
        self._dual_to_range = dual_to_range
        self._regular_order = regular_order
        self._singular_order = singular_order
        self._expansion_order = expansion_order

        self._local_points, self._weights = rule(regular_order)

        hmax = _np.max(
            [
                domain.grid.maximum_element_diameter,
                dual_to_range.grid.maximum_element_diameter,
            ]
        )

        domain_box = domain.grid.bounding_box
        dual_to_range_box = dual_to_range.grid.bounding_box

        merged_box = _np.array(
            [
                _np.minimum(domain_box[:, 0], dual_to_range_box[:, 0]),
                _np.maximum(domain_box[:, 1], dual_to_range_box[:, 1]),
            ]
        ).T
        center = (merged_box[:, 0] + merged_box[:, 1]) / 2
        radius = (
            _np.maximum(
                _np.max(center - merged_box[:, 0]), _np.max(merged_box[:, 1] - center)
            )
            * 1.00001
        )

        if max_level == -1:
            max_level = int(_np.log2(2 * radius) - _np.log2(hmax))

        if max_level < 0:
            raise ValueError("Could not correctly determine maximum level.")

        exafmm_laplace.configure(expansion_order, ncritical, max_level)

        self._setup_tree()

        self._source_transform = self._map_space_to_points(
            self._domain, self._local_points, self._weights, "source"
        )

        self._target_transform = self._map_space_to_points(
            self._domain, self._local_points, self._weights, "target"
        )

        self._compute_near_field_matrix()

    def _compute_near_field_matrix(self):
        """Compute the near-field matrix."""
        from bempp.api.operators.boundary.laplace import single_layer
        from scipy.sparse import coo_matrix

        near_targets, near_sources = self._collect_near_field_indices(
            self._local_points.shape[1]
        )

        data = 1.0 / (
            4
            * _np.pi
            * _np.linalg.norm(
                self.targets[near_targets] - self.sources[near_sources], axis=1
            )
        )

        interactions = coo_matrix(
            (data, (near_targets, near_sources)),
            shape=(len(self.targets), len(self.sources)),
        ).tocsr()

        singular_interactions = single_layer(
            self._domain,
            self._domain,
            self._dual_to_range,
            assembler="only_singular_part",
        ).weak_form().A

        self._near_field_matrix = (
            self._target_transform.T @ interactions @ self._source_transform
            + singular_interactions
        )

    @property
    def nodes(self):
        """Return the nodes."""
        return self._nodes

    @property
    def leaf_node_keys(self):
        """Return leaf nodes."""
        return self._leaf_nodes

    @property
    def source_transform(self):
        """Return source transformation matrix."""
        return self._source_transform

    @property
    def target_transform(self):
        """Return target transformation matrix."""
        return self._target_transform

    @property
    def source_grid(self):
        """Return source grid."""
        return self._domain.grid

    @property
    def target_grid(self):
        """Return target grid."""
        return self._dual_to_range.grid

    @property
    def sources(self):
        """Return sources."""
        return self._sources

    @property
    def targets(self):
        """Return target."""
        return self._targets

    def _setup_tree(self):
        """Setup the FMM tree."""
        from .common import Node
        from .common import grid_to_points

        from exafmm_laplace import init_sources
        from exafmm_laplace import init_targets
        from exafmm_laplace import build_tree
        from exafmm_laplace import build_list

        self._sources = grid_to_points(
            self._domain.grid, self._domain.support_elements, self._local_points
        )
        self._targets = grid_to_points(
            self._dual_to_range.grid,
            self._dual_to_range.support_elements,
            self._local_points,
        )
        source_bodies = init_sources(
            self._sources, _np.zeros(len(self._sources), dtype=_np.float64)
        )
        target_bodies = init_targets(self._targets)
        build_tree(source_bodies, target_bodies)
        exafmm_nodes = build_list()

        for exafmm_node in exafmm_nodes:
            self._nodes[exafmm_node.key] = Node(
                exafmm_node.key,
                _np.array(
                    [exafmm_node.x[0], exafmm_node.x[1], exafmm_node.x[2]],
                    dtype="float64",
                ),
                exafmm_node.r,
                exafmm_node.isrcs,
                exafmm_node.itrgs,
                [
                    node.key if node is not None else None
                    for node in exafmm_node.colleagues
                ],
                exafmm_node.is_leaf,
                exafmm_node.level,
                exafmm_node.parent.key if exafmm_node.parent is not None else None,
            )

        self._leaf_nodes = [key for (key, node) in self._nodes.items() if node.is_leaf]
#
# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Utilities for ray tracing"""

import drjit as dr
import mitsuba as mi
from typing import Callable

from sionna.rt.constants import EPSILON_FLOAT


def fibonacci_lattice(num_points : int) -> mi.Point2f:
    r"""
    Generates a Fibonacci lattice of size ``num_points`` on the unit square
    :math:`[0, 1] \times [0, 1]`

    :param num_points: Size of the lattice
    """

    golden_ratio = (1.+dr.sqrt(mi.Float64(5.)))/2.
    ns = dr.arange(mi.Float64, 0, num_points)

    x = ns/golden_ratio
    x = x - dr.floor(x)
    y = ns/(num_points-1)

    return mi.Point2f(x, y)

def spawn_ray_from_sources(
    lattice : Callable[[int], mi.Point2f],
    samples_per_src : int,
    src_positions : mi.Point3f
) -> mi.Ray3f:
    r"""
    Spawns ``samples_per_src`` rays for each source at the positions specified
    by ``src_positions``, oriented in the directions defined by the ``lattice``

    The spawned rays are ordered samples-first.

    :param lattice: Callable that generates the lattice used as directions for
        the rays
    :param samples_per_src: Number of rays per source to spawn
    :param src_positions: Positions of the sources
    """

    num_sources = dr.shape(src_positions)[1]

    # Ray directions
    samples_on_square = lattice(samples_per_src)
    k_world = mi.warp.square_to_uniform_sphere(samples_on_square)

    # Samples-first ordering is used, i.e., the samples are ordered as
    # follows:
    # [source_0_samples..., source_1_samples..., ...]
    # Each source has its own lattice
    k_world = dr.tile(k_world, num_sources)
    # Rays origins are the source locations
    origins = dr.repeat(src_positions, samples_per_src)

    # Spawn rays from the sources
    ray = mi.Ray3f(o=origins, d=k_world)
    # Minor workaround to avoid loop retracing due to size mismatch.
    ray.time = dr.zeros(mi.Float, dr.width(k_world))

    return ray

def offset_p(p : mi.Point3f, d : mi.Vector3f, n : mi.Vector3f) -> mi.Point3f:
    # pylint: disable=line-too-long
    r"""
    Adds a small offset to :math:`\mathbf{p}` along :math:`\mathbf{n}` such that
    :math:`\mathbf{n}^{\textsf{T}} \mathbf{d} \gt 0`

    More precisely, this function returns :math:`\mathbf{o}` such that:

    .. math::
        \mathbf{o} = \mathbf{p} + \epsilon\left(1 + \max{\left\{|p_x|,|p_y|,|p_z|\right\}}\right)\texttt{sign}(\mathbf{d} \cdot \mathbf{n})\mathbf{n}

    where :math:`\epsilon` depends on the numerical precision and :math:`\mathbf{p} = (p_x,p_y,p_z)`.

    :param p: Point to offset
    :param d: Direction toward which to offset along ``n``
    :param n: Direction along which to offset
    """

    a = (1. + dr.max(dr.abs(p), axis=0)) * EPSILON_FLOAT
    # Detach this operation to ensure these is no gradient computation
    a = dr.detach(dr.mulsign(a, dr.dot(d,n)))
    po = dr.fma(a, n, p)
    return po

def spawn_ray_towards(
    p : mi.Point3f,
    t : mi.Point3f,
    n : mi.Vector3f | None = None
) -> mi.Ray3f:
    r"""
    Spawns a ray with infinite length from :math:`\mathbf{p}` toward
    :math:`\mathbf{t}`

    If :math:`\mathbf{n}` is not :py:class:`None`, then a small offset is added
    to :math:`\mathbf{p}` along :math:`\mathbf{n}` in the direction of
    :math:`\mathbf{t}`.

    :param p: Origin of the ray
    :param t: Point towards which to spawn the ray
    :param n: (Optional) Direction along which to offset :math:`\mathbf{p}`
    """

    # Adds a small offset to `p` to avoid self-intersection
    if n is None:
        po = p
    else:
        po = offset_p(p, t - p, n)
    # Ray direction towards `t`
    d = dr.normalize(t - po)
    #
    ray = mi.Ray3f(po, d)
    return ray

def spawn_ray_to(
    p : mi.Point3f,
    t : mi.Point3f,
    n : mi.Vector3f | None = None
) -> mi.Ray3f:
    r"""
    Spawns a finite ray from :math:`\mathbf{p}` to :math:`\mathbf{t}`

    The length of the ray is set to :math:`\|\mathbf{p} - \mathbf{t}\|`.

    If :math:`\mathbf{n}` is not :py:class:`None`, then a small offset is added
    to :math:`\mathbf{p}` along :math:`\mathbf{n}` in the direction of
    :math:`\mathbf{t}`.

    :param p: Origin of the ray
    :param t: Point towards which to spawn the ray
    :param n: (Optional) Direction along which to offset :math:`\mathbf{p}`
    """

    # Adds a small offset to `p`
    if n is None:
        po = p
    else:
        po = offset_p(p, t - p, n)
    # Ray direction towards `t`
    d = t - po
    maxt = dr.norm(d)
    d /= maxt
    maxt *= (1. - EPSILON_FLOAT)
    #
    ray = mi.Ray3f(po, d,  maxt=maxt, time=0., wavelengths=mi.Color0f())
    return ray

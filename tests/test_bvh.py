# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from animated_drawings.model.bvh import BVH
from pkg_resources import resource_filename


def test_bvh_from_file():
    bvh_fn = resource_filename(__name__, 'test_bvh_files/zombie.bvh')
    b = BVH.from_file(bvh_fn)

    # was the skeleton built correctly?
    assert b.root_joint.joint_count() == 34

    # did frame_time parse correctly?
    assert b.frame_time == 0.0333333

    # did frame num parse correctly?
    assert b.frame_max_num == 779

    # there should be root position data for each frame
    assert b.frame_max_num == b.pos_data.shape[0]
    # and it should be an xzy coordinate
    assert b.pos_data.shape[-1] == 3

    # there should be rotation data for each frame
    assert b.frame_max_num == b.rot_data.shape[0]
    # there should be a rotation for every joint within that frame
    assert b.rot_data.shape[1] == b.root_joint.joint_count()
    # and the rotation is a quaternion with dimensionality of 4
    assert b.rot_data.shape[-1] == 4

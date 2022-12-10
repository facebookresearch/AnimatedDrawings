from model.bvh import BVH


def test_bvh_from_file():
    bvh_fn = 'animate/animator/tests/zombie.bvh'
    b = BVH.from_file(bvh_fn)

    # was the skeleton built correctly?
    assert BVH.joint_count(b.root_joint) == 34

    # did frame_time parse correctly?
    assert b.frame_time == 0.0333333

    # did frame num parse correctly?
    assert b.frame_num == 779

    # there should be root position data for each frame
    assert b.frame_num == b.pos_data.shape[0]
    # and it should be an xzy coordinate
    assert b.pos_data.shape[-1] == 3

    # there should be rotation data for each frame
    assert b.frame_num == b.rot_data.shape[0]
    # there should be a rotation for every joint within that frame
    assert b.rot_data.shape[1] == BVH.joint_count(b.root_joint)
    # and the rotation is a quaternion with dimensionality of 4
    assert b.rot_data.shape[-1] == 4


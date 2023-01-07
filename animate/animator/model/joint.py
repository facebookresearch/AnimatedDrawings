from model.transform import Transform


class Joint(Transform):
    """
    Skeletal joint used representing character poses.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def joint_count(self):
        """ Returns the number of Joint children in this joint's kinematic chain(recursive) """
        count = 1
        for c in self.get_children():
            if isinstance(c, Joint):
                count += c.joint_count()
        return count
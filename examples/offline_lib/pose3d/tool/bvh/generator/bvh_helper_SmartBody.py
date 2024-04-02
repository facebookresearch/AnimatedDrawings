import os
from pathlib import Path


class BvhNode(object):
    def __init__(
            self, name, offset, rotation_order,
            children=None, parent=None, is_root=False, is_end_site=False ):
        if not is_end_site and \
                rotation_order not in ['xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx']:
            raise ValueError(f'Rotation order invalid.')
        self.name = name
        self.offset = offset
        self.rotation_order = rotation_order
        self.children = children
        self.parent = parent
        self.is_root = is_root
        self.is_end_site = is_end_site


class BvhHeader(object):
    def __init__(self, root, nodes):
        self.root = root
        self.nodes = nodes


def write_header(writer, node, level):
    indent = ' ' * 4 * level
    if node.is_root:
        writer.write(f'{indent}ROOT {node.name}\n')
        channel_num = 6
    elif node.is_end_site:
        writer.write(f'{indent}End Site\n')
        channel_num = 0
    else:
        writer.write(f'{indent}JOINT {node.name}\n')
        channel_num = 3
    writer.write(f'{indent}{"{"}\n')

    indent = ' ' * 4 * (level + 1)
    writer.write(
        f'{indent}OFFSET '
        f'{node.offset[0]} {node.offset[1]} {node.offset[2]}\n'
    )
    if channel_num:
        channel_line = f'{indent}CHANNELS {channel_num} '
        if node.is_root:
            channel_line += f'Xposition Yposition Zposition '
        channel_line += ' '.join([
            f'{axis.upper()}rotation'
            for axis in node.rotation_order
        ])
        writer.write(channel_line + '\n')

    for child in node.children:
        write_header(writer, child, level + 1)

    indent = ' ' * 4 * level
    writer.write(f'{indent}{"}"}\n')

def write_bvh(output_file, header, channels, frame_rate=30):
    output_file = Path(output_file)
    if not output_file.parent.exists():
        os.makedirs(output_file.parent)

    with output_file.open('w') as f:
        f.write('HIERARCHY\n')
        write_header(writer=f, node=header.root, level=0)

        f.write('MOTION\n')
        f.write(f'Frames: {len(channels)}\n')
        f.write(f'Frame Time: {1 / frame_rate}\n')

        for channel in channels:
            f.write(' '.join([f'{element}' for element in channel]) + '\n')
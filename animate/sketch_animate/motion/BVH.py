import re
import numpy as np

from sketch_animate.motion.Animation import Animation
from sketch_animate.motion.Quaternions import Quaternions

channelmap = {
    'Xrotation' : 'x',
    'Yrotation' : 'y',
    'Zrotation' : 'z'   
}

channelmap_inv = {
    'x': 'Xrotation',
    'y': 'Yrotation',
    'z': 'Zrotation',
}

ordermap = {
    'x' : 0,
    'y' : 1,
    'z' : 2,
}

def load(filename, start=None, end=None, order=None, world=False):
    """
    Reads a BVH file and constructs an animation
    
    Parameters
    ----------
    filename: str
        File to be opened
        
    start : int
        Optional Starting Frame
        
    end : int
        Optional Ending Frame
    
    order : str
        Optional Specifier for joint order.
        Given as string E.G 'xyz', 'zxy'
        
    world : bool
        If set to true euler angles are applied
        together in world space rather than local
        space

    Returns
    -------
    
    (animation, joint_names, frametime)
        Tuple of loaded animation and joint names
    """


    if 'cmu_new2' in filename:  # files in cmu_new have extra position data on some joints that must be removed
        cmu_new2 = True
    else:
        cmu_new2 = False
    
    f = open(filename, "r")

    i = 0
    active = -1
    end_site = False
    
    names = []
    orients = Quaternions.id(0)
    offsets = np.array([]).reshape((0,3))
    parents = np.array([], dtype=int)

    orders = []
    for line in f:
        
        if "HIERARCHY" in line: continue
        if "MOTION" in line: continue

        rmatch = re.match(r"ROOT (\w+)", line)
        if rmatch:
            names.append(rmatch.group(1))
            offsets    = np.append(offsets,    np.array([[0,0,0]]),   axis=0)
            orients.qs = np.append(orients.qs, np.array([[1,0,0,0]]), axis=0)
            parents    = np.append(parents, active)
            active = (len(parents)-1)
            continue

        if "{" in line: continue

        if "}" in line:
            if end_site: end_site = False
            else: active = parents[active]
            continue
        
        offmatch = re.match(r"\s*OFFSET\s+([\-\d\.e]+)\s+([\-\d\.e]+)\s+([\-\d\.e]+)", line)
        if offmatch:
            if not end_site:
                offsets[active] = np.array([list(map(float, offmatch.groups()))])
            continue
           
        chanmatch = re.match(r"\s*CHANNELS\s+(\d+)", line)
        if chanmatch:
            channels = int(chanmatch.group(1))
            if order is None:
                channelis = 0 if channels == 3 else 3
                channelie = 3 if channels == 3 else 6
                parts = line.split()[2+channelis:2+channelie]
                if any([p not in channelmap for p in parts]):
                    continue
                order = "".join([channelmap[p] for p in parts])
                orders.append(order)
                order = None
            continue

        jmatch = re.match("\s*JOINT\s+(\w+)", line)
        if jmatch:
            names.append(jmatch.group(1))
            offsets    = np.append(offsets,    np.array([[0,0,0]]),   axis=0)
            orients.qs = np.append(orients.qs, np.array([[1,0,0,0]]), axis=0)
            parents    = np.append(parents, active)
            active = (len(parents)-1)
            continue
        
        if "End Site" in line:
            end_site = True
            continue
              
        fmatch = re.match("\s*Frames:\s+(\d+)", line)
        if fmatch:
            if start and end:
                fnum = (end - start)-1
            else:
                fnum = int(fmatch.group(1))
            jnum = len(parents)
            positions = offsets[np.newaxis].repeat(fnum, axis=0)
            rotations = np.zeros((fnum, len(orients), 3))
            continue
        
        fmatch = re.match("\s*Frame Time:\s+([\d\.]+)", line)
        if fmatch:
            frametime = float(fmatch.group(1))
            continue
        
        if (start and end) and (i < start or i >= end-1):
            i += 1
            continue
        
        dmatch = line.strip().split(' ')
        if dmatch:
            data_block = np.array(list(map(float, dmatch)))
            N = len(parents)
            fi = i - start if start else i
            if   channels == 3:
                positions[fi,0:1] = data_block[0:3]
                if cmu_new2:
                    rotation_dimensions = np.r_[3:30, 33:36, 39:66]
                    rotations[fi, : ] = data_block[rotation_dimensions].reshape(N,3)
                else:
                    rotations[fi, : ] = data_block[3: ].reshape(N,3)
            elif channels == 6:
                data_block = data_block.reshape(N,6)
                positions[fi,:] = data_block[:,0:3]
                rotations[fi,:] = data_block[:,3:6]
            elif channels == 9:
                positions[fi,0] = data_block[0:3]
                data_block = data_block[3:].reshape(N-1,9)
                rotations[fi,1:] = data_block[:,3:6]
                positions[fi,1:] += data_block[:,0:3] * data_block[:,6:9]
            else:
                raise Exception("Too many channels! %i" % channels)

            i += 1

    f.close()

    _ = Quaternions.from_euler(np.radians(rotations), order='xyz', world=world)
    for joint in range(rotations.shape[1]):
        _[:,joint] = Quaternions.from_euler(np.radians(rotations[:,joint,:]), order=orders[joint], world=world)
    rotations = _

    return (Animation(rotations, positions, orients, offsets, parents), names, frametime)
    

    
def save(filename, anim, names=None, frametime=1.0/24.0, order='zyx', positions=False, orients=True):
    """
    Saves an Animation to file as BVH
    
    Parameters
    ----------
    filename: str
        File to be saved to
        
    anim : Animation
        Animation to save
        
    names : [str]
        List of joint names
    
    order : str
        Optional Specifier for joint order.
        Given as string E.G 'xyz', 'zxy'
    
    frametime : float
        Optional Animation Frame time
        
    positions : bool
        Optional specfier to save bone
        positions for each frame
        
    orients : bool
        Multiply joint orients to the rotations
        before saving.
        
    """
    
    if names is None:
        names = ["joint_" + str(i) for i in range(len(anim.parents))]
    
    with open(filename, 'w') as f:

        t = ""
        f.write("%sHIERARCHY\n" % t)
        f.write("%sROOT %s\n" % (t, names[0]))
        f.write("%s{\n" % t)
        t += '\t'

        f.write("%sOFFSET %f %f %f\n" % (t, anim.offsets[0,0], anim.offsets[0,1], anim.offsets[0,2]) )
        f.write("%sCHANNELS 6 Xposition Yposition Zposition %s %s %s \n" % 
            (t, channelmap_inv[order[0]], channelmap_inv[order[1]], channelmap_inv[order[2]]))

        for i in range(anim.shape[1]):
            if anim.parents[i] == 0:
                t = save_joint(f, anim, names, t, i, order=order, positions=positions)

        t = t[:-1]
        f.write("%s}\n" % t)

        f.write("MOTION\n")
        f.write("Frames: %i\n" % anim.shape[0]);
        f.write("Frame Time: %f\n" % frametime);
            
        #if orients:        
        #    rots = np.degrees((-anim.orients[np.newaxis] * anim.rotations).euler(order=order[::-1]))
        #else:
        #    rots = np.degrees(anim.rotations.euler(order=order[::-1]))
        rots = np.degrees(anim.rotations.euler(order=order[::-1]))
        poss = anim.positions
        
        for i in range(anim.shape[0]):
            for j in range(anim.shape[1]):
                
                if positions or j == 0:
                
                    f.write("%f %f %f %f %f %f " % (
                        poss[i,j,0],                  poss[i,j,1],                  poss[i,j,2], 
                        rots[i,j,ordermap[order[0]]], rots[i,j,ordermap[order[1]]], rots[i,j,ordermap[order[2]]]))
                
                else:
                    
                    f.write("%f %f %f " % (
                        rots[i,j,ordermap[order[0]]], rots[i,j,ordermap[order[1]]], rots[i,j,ordermap[order[2]]]))

            f.write("\n")
    
    
def save_joint(f, anim, names, t, i, order='zyx', positions=False):
    
    f.write("%sJOINT %s\n" % (t, names[i]))
    f.write("%s{\n" % t)
    t += '\t'
  
    f.write("%sOFFSET %f %f %f\n" % (t, anim.offsets[i,0], anim.offsets[i,1], anim.offsets[i,2]))
    
    if positions:
        f.write("%sCHANNELS 6 Xposition Yposition Zposition %s %s %s \n" % (t, 
            channelmap_inv[order[0]], channelmap_inv[order[1]], channelmap_inv[order[2]]))
    else:
        f.write("%sCHANNELS 3 %s %s %s\n" % (t, 
            channelmap_inv[order[0]], channelmap_inv[order[1]], channelmap_inv[order[2]]))
    
    end_site = True
    
    for j in range(anim.shape[1]):
        if anim.parents[j] == i:
            t = save_joint(f, anim, names, t, j, order=order, positions=positions)
            end_site = False
    
    if end_site:
        f.write("%sEnd Site\n" % t)
        f.write("%s{\n" % t)
        t += '\t'
        f.write("%sOFFSET %f %f %f\n" % (t, 0.0, 0.0, 0.0))
        t = t[:-1]
        f.write("%s}\n" % t)
  
    t = t[:-1]
    f.write("%s}\n" % t)
    
    return t

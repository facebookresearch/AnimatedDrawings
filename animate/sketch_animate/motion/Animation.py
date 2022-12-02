import operator

import numpy as np
import numpy.core.umath_tests as ut

#import AnimationStructure
from sketch_animate.motion.Quaternions import Quaternions

class Animation:
    """
    Animation is a numpy-like wrapper for animation data
    
    Animation data consists of several arrays consisting
    of F frames and J joints.
    
    The animation is specified by
    
        rotations : (F, J) Quaternions | Joint Rotations
        positions : (F, J, 3) ndarray  | Joint Positions
    
    The base pose is specified by
    
        orients   : (J) Quaternions    | Joint Orientations
        offsets   : (J, 3) ndarray     | Joint Offsets
        
    And the skeletal structure is specified by
        
        parents   : (J) ndarray        | Joint Parents
    """
    
    def __init__(self, rotations, positions, orients, offsets, parents):
        
        self.rotations = rotations
        self.positions = positions
        self.orients   = orients
        self.offsets   = offsets
        self.parents   = parents
    
    def __op__(self, op, other):
        return Animation(
            op(self.rotations, other.rotations),
            op(self.positions, other.positions),
            op(self.orients, other.orients),
            op(self.offsets, other.offsets),
            op(self.parents, other.parents))

    def __iop__(self, op, other):
        self.rotations = op(self.roations, other.rotations)
        self.positions = op(self.roations, other.positions)
        self.orients   = op(self.orients, other.orients)
        self.offsets   = op(self.offsets, other.offsets)
        self.parents   = op(self.parents, other.parents)
        return self
    
    def __sop__(self, op):
        return Animation(
            op(self.rotations),
            op(self.positions),
            op(self.orients),
            op(self.offsets),
            op(self.parents))
    
    def __add__(self, other): return self.__op__(operator.add, other)
    def __sub__(self, other): return self.__op__(operator.sub, other)
    def __mul__(self, other): return self.__op__(operator.mul, other)
    def __div__(self, other): return self.__op__(operator.div, other)
    
    def __abs__(self): return self.__sop__(operator.abs)
    def __neg__(self): return self.__sop__(operator.neg)
    
    def __iadd__(self, other): return self.__iop__(operator.iadd, other)
    def __isub__(self, other): return self.__iop__(operator.isub, other)
    def __imul__(self, other): return self.__iop__(operator.imul, other)
    def __idiv__(self, other): return self.__iop__(operator.idiv, other)
    
    def __len__(self): return len(self.rotations)
    
    def __getitem__(self, k):
        if isinstance(k, tuple):
            return Animation(
                self.rotations[k],
                self.positions[k],
                self.orients[k[1:]],
                self.offsets[k[1:]],
                self.parents[k[1:]]) 
        else:
            return Animation(
                self.rotations[k],
                self.positions[k],
                self.orients,
                self.offsets,
                self.parents) 
        
    def __setitem__(self, k, v): 
        if isinstance(k, tuple):
            self.rotations.__setitem__(k, v.rotations)
            self.positions.__setitem__(k, v.positions)
            self.orients.__setitem__(k[1:], v.orients)
            self.offsets.__setitem__(k[1:], v.offsets)
            self.parents.__setitem__(k[1:], v.parents)
        else:
            self.rotations.__setitem__(k, v.rotations)
            self.positions.__setitem__(k, v.positions)
            self.orients.__setitem__(k, v.orients)
            self.offsets.__setitem__(k, v.offsets)
            self.parents.__setitem__(k, v.parents)
        
    @property
    def shape(self): return (self.rotations.shape[0], self.rotations.shape[1])
            
    def copy(self): return Animation(
        self.rotations.copy(), self.positions.copy(), 
        self.orients.copy(), self.offsets.copy(), 
        self.parents.copy())
    
    def repeat(self, *args, **kw):
        return Animation(
            self.rotations.repeat(*args, **kw),
            self.positions.repeat(*args, **kw),
            self.orients, self.offsets, self.parents)
        
    def ravel(self):
        return np.hstack([
            self.rotations.log().ravel(),
            self.positions.ravel(),
            self.orients.log().ravel(),
            self.offsets.ravel()])
        
    @classmethod
    def unravel(clas, anim, shape, parents):
        nf, nj = shape
        rotations = anim[nf*nj*0:nf*nj*3]
        positions = anim[nf*nj*3:nf*nj*6]
        orients   = anim[nf*nj*6+nj*0:nf*nj*6+nj*3]
        offsets   = anim[nf*nj*6+nj*3:nf*nj*6+nj*6]
        return cls(
            Quaternions.exp(rotations), positions,
            Quaternions.exp(orients), offsets,
            parents.copy())
    
    
""" Maya Interaction """

#def load_to_maya(anim, names=None, radius=0.5):
#    """
#    Load Animation Object into Maya as Joint Skeleton
#    loads each frame as a new keyfame in maya.
#
#    If the animation is too slow or too fast perhaps
#    the framerate needs adjusting before being loaded
#    such that it matches the maya scene framerate.
#
#
#    Parameters
#    ----------
#
#    anim : Animation
#        Animation to load into Scene
#
#    names : [str]
#        Optional list of Joint names for Skeleton
#
#    Returns
#    -------
#
#    List of Maya Joint Nodes loaded into scene
#    """
#
#    import pymel.core as pm
#
#    joints = []
#    frames = range(1, len(anim)+1)
#
#    if names is None: names = ["joint_" + str(i) for i in range(len(anim.parents))]
#
#    for i, offset, orient, parent, name in zip(range(len(anim.offsets)), anim.offsets, anim.orients, anim.parents, names):
#
#        if parent < 0:
#            pm.select(d=True)
#        else:
#            pm.select(joints[parent])
#
#        joint = pm.joint(n=name, p=offset, relative=True, radius=radius)
#        joint.setOrientation([orient[1], orient[2], orient[3], orient[0]])
#
#        curvex = pm.nodetypes.AnimCurveTA(n=name + "_rotateX")
#        curvey = pm.nodetypes.AnimCurveTA(n=name + "_rotateY")
#        curvez = pm.nodetypes.AnimCurveTA(n=name + "_rotateZ")
#
#        jrotations = (-Quaternions(orient[np.newaxis]) * anim.rotations[:,i]).euler()
#        curvex.addKeys(frames, jrotations[:,0])
#        curvey.addKeys(frames, jrotations[:,1])
#        curvez.addKeys(frames, jrotations[:,2])
#
#        pm.connectAttr(curvex.output, joint.rotateX)
#        pm.connectAttr(curvey.output, joint.rotateY)
#        pm.connectAttr(curvez.output, joint.rotateZ)
#
#        offsetx = pm.nodetypes.AnimCurveTU(n=name + "_translateX")
#        offsety = pm.nodetypes.AnimCurveTU(n=name + "_translateY")
#        offsetz = pm.nodetypes.AnimCurveTU(n=name + "_translateZ")
#
#        offsetx.addKeys(frames, anim.positions[:,i,0])
#        offsety.addKeys(frames, anim.positions[:,i,1])
#        offsetz.addKeys(frames, anim.positions[:,i,2])
#
#        pm.connectAttr(offsetx.output, joint.translateX)
#        pm.connectAttr(offsety.output, joint.translateY)
#        pm.connectAttr(offsetz.output, joint.translateZ)
#
#        joints.append(joint)
#
#    return joints

def load_from_maya(root, start, end):
    """
    Load Animation Object from Maya Joint Skeleton    
    
    Parameters
    ----------
    
    root : PyNode
        Root Joint of Maya Skeleton
        
    start, end : int, int
        Start and End frame index of Maya Animation
    
    Returns
    -------
    
    animation : Animation
        Loaded animation from maya
        
    names : [str]
        Joint names from maya   
    """

    import pymel.core as pm
    
    original_time = pm.currentTime(q=True)
    pm.currentTime(start)
    
    """ Build Structure """
    
    names, parents = AnimationStructure.load_from_maya(root)
    descendants = AnimationStructure.descendants_list(parents)
    orients = Quaternions.id(len(names))
    offsets = np.array([pm.xform(j, q=True, translation=True) for j in names])
    
    for j, name in enumerate(names):
        scale = pm.xform(pm.PyNode(name), q=True, scale=True, relative=True)
        if len(descendants[j]) == 0: continue
        offsets[descendants[j]] *= scale
    
    """ Load Animation """

    eulers    = np.zeros((end-start, len(names), 3))
    positions = np.zeros((end-start, len(names), 3))
    rotations = Quaternions.id((end-start, len(names)))
    
    for i in range(end-start):
        
        pm.currentTime(start+i+1, u=True)
        
        scales = {}
        
        for j, name, parent in zip(range(len(names)), names, parents):
            
            node = pm.PyNode(name)
            
            if i == 0 and pm.hasAttr(node, 'jointOrient'):
                ort = node.getOrientation()
                orients[j] = Quaternions(np.array([ort[3], ort[0], ort[1], ort[2]]))
            
            if pm.hasAttr(node, 'rotate'):    eulers[i,j]    = np.radians(pm.xform(node, q=True, rotation=True))
            if pm.hasAttr(node, 'translate'): positions[i,j] = pm.xform(node, q=True, translation=True)
            if pm.hasAttr(node, 'scale'):     scales[j]      = pm.xform(node, q=True, scale=True, relative=True)

        for j in scales:
            if len(descendants[j]) == 0: continue
            positions[i,descendants[j]] *= scales[j] 
        
        positions[i,0] = pm.xform(root, q=True, translation=True, worldSpace=True)
    
    rotations = orients[np.newaxis] * Quaternions.from_euler(eulers, order='xyz', world=True)
    
    """ Done """
    
    pm.currentTime(original_time)
    
    return Animation(rotations, positions, orients, offsets, parents), names
    
    
def transforms_local(anim):
    """
    Computes Animation Local Transforms
    
    As well as a number of other uses this can
    be used to compute global joint transforms,
    which in turn can be used to compete global
    joint positions
    
    Parameters
    ----------
    
    anim : Animation
        Input animation
        
    Returns
    -------
    
    transforms : (F, J, 4, 4) ndarray
    
        For each frame F, joint local
        transforms for each joint J
    """
    
    transforms = anim.rotations.transforms()
    transforms = np.concatenate([transforms, np.zeros(transforms.shape[:2] + (3, 1))], axis=-1)
    transforms = np.concatenate([transforms, np.zeros(transforms.shape[:2] + (1, 4))], axis=-2)
    transforms[:,:,0:3,3] = anim.positions
    transforms[:,:,3:4,3] = 1.0
    return transforms

    
def transforms_multiply(t0s, t1s):
    """
    Transforms Multiply
    
    Multiplies two arrays of animation transforms
    
    Parameters
    ----------
    
    t0s, t1s : (F, J, 4, 4) ndarray
        Two arrays of transforms
        for each frame F and each
        joint J
        
    Returns
    -------
    
    transforms : (F, J, 4, 4) ndarray
        Array of transforms for each
        frame F and joint J multiplied
        together
    """
    
    return ut.matrix_multiply(t0s, t1s)
    
def transforms_inv(ts):
    fts = ts.reshape(-1, 4, 4)
    fts = np.array(list(map(lambda x: np.linalg.inv(x), fts)))
    return fts.reshape(ts.shape)
    
def transforms_blank(anim):
    """
    Blank Transforms
    
    Parameters
    ----------
    
    anim : Animation
        Input animation
    
    Returns
    -------
    
    transforms : (F, J, 4, 4) ndarray
        Array of identity transforms for 
        each frame F and joint J
    """

    ts = np.zeros(anim.shape + (4, 4)) 
    ts[:,:,0,0] = 1.0; ts[:,:,1,1] = 1.0;
    ts[:,:,2,2] = 1.0; ts[:,:,3,3] = 1.0;
    return ts
    
def transforms_global(anim):
    """
    Global Animation Transforms
    
    This relies on joint ordering
    being incremental. That means a joint
    J1 must not be a ancestor of J0 if
    J0 appears before J1 in the joint
    ordering.
    
    Parameters
    ----------
    
    anim : Animation
        Input animation
    
    Returns
    ------
    
    transforms : (F, J, 4, 4) ndarray
        Array of global transforms for 
        each frame F and joint J
    """
    
    joints  = np.arange(anim.shape[1])
    parents = np.arange(anim.shape[1])
    locals  = transforms_local(anim)
    globals = transforms_blank(anim)

    globals[:,0] = locals[:,0]
    
    for i in range(1, anim.shape[1]):
        globals[:,i] = transforms_multiply(globals[:,anim.parents[i]], locals[:,i])
        
    return globals
    
    
def positions_global(anim):
    """
    Global Joint Positions
    
    Given an animation compute the global joint
    positions at at every frame
    
    Parameters
    ----------
    
    anim : Animation
        Input animation
        
    Returns
    -------
    
    positions : (F, J, 3) ndarray
        Positions for every frame F 
        and joint position J
    """
    
    positions = transforms_global(anim)[:,:,:,3]
    return positions[:,:,:3] / positions[:,:,3,np.newaxis]
    
""" Rotations """
    
def rotations_global(anim):
    """
    Global Animation Rotations
    
    This relies on joint ordering
    being incremental. That means a joint
    J1 must not be a ancestor of J0 if
    J0 appears before J1 in the joint
    ordering.
    
    Parameters
    ----------
    
    anim : Animation
        Input animation
        
    Returns
    -------
    
    points : (F, J) Quaternions
        global rotations for every frame F 
        and joint J
    """

    joints  = np.arange(anim.shape[1])
    parents = np.arange(anim.shape[1])
    locals  = anim.rotations
    globals = Quaternions.id(anim.shape)
    
    globals[:,0] = locals[:,0]
    
    for i in range(1, anim.shape[1]):
        globals[:,i] = globals[:,anim.parents[i]] * locals[:,i]
        
    return globals
    
def rotations_parents_global(anim):
    rotations = rotations_global(anim)
    rotations = rotations[:,anim.parents]
    rotations[:,0] = Quaternions.id(len(anim))
    return rotations
    
def rotations_load_to_maya(rotations, positions, names=None):
    """
    Load Rotations into Maya
    
    Loads a Quaternions array into the scene
    via the representation of axis
    
    Parameters
    ----------
    
    rotations : (F, J) Quaternions 
        array of rotations to load
        into the scene where
            F = number of frames
            J = number of joints
    
    positions : (F, J, 3) ndarray 
        array of positions to load
        rotation axis at where:
            F = number of frames
            J = number of joints
            
    names : [str]
        List of joint names
    
    Returns
    -------
    
    maxies : Group
        Grouped Maya Node of all Axis nodes
    """
    
    import pymel.core as pm

    if names is None: names = ["joint_" + str(i) for i in range(rotations.shape[1])]
    
    maxis = []
    frames = range(1, len(positions)+1)
    for i, name in enumerate(names):
    
        name = name + "_axis"
        axis = pm.group(
             pm.curve(p=[(0,0,0), (1,0,0)], d=1, n=name+'_axis_x'),
             pm.curve(p=[(0,0,0), (0,1,0)], d=1, n=name+'_axis_y'),
             pm.curve(p=[(0,0,0), (0,0,1)], d=1, n=name+'_axis_z'),
             n=name)
        
        axis.rotatePivot.set((0,0,0))
        axis.scalePivot.set((0,0,0))
        axis.childAtIndex(0).overrideEnabled.set(1); axis.childAtIndex(0).overrideColor.set(13)
        axis.childAtIndex(1).overrideEnabled.set(1); axis.childAtIndex(1).overrideColor.set(14)
        axis.childAtIndex(2).overrideEnabled.set(1); axis.childAtIndex(2).overrideColor.set(15)
    
        curvex = pm.nodetypes.AnimCurveTA(n=name + "_rotateX")
        curvey = pm.nodetypes.AnimCurveTA(n=name + "_rotateY")
        curvez = pm.nodetypes.AnimCurveTA(n=name + "_rotateZ")  
        
        arotations = rotations[:,i].euler()
        curvex.addKeys(frames, arotations[:,0])
        curvey.addKeys(frames, arotations[:,1])
        curvez.addKeys(frames, arotations[:,2])
        
        pm.connectAttr(curvex.output, axis.rotateX)
        pm.connectAttr(curvey.output, axis.rotateY)
        pm.connectAttr(curvez.output, axis.rotateZ)
        
        offsetx = pm.nodetypes.AnimCurveTU(n=name + "_translateX")
        offsety = pm.nodetypes.AnimCurveTU(n=name + "_translateY")
        offsetz = pm.nodetypes.AnimCurveTU(n=name + "_translateZ")
        
        offsetx.addKeys(frames, positions[:,i,0])
        offsety.addKeys(frames, positions[:,i,1])
        offsetz.addKeys(frames, positions[:,i,2])
        
        pm.connectAttr(offsetx.output, axis.translateX)
        pm.connectAttr(offsety.output, axis.translateY)
        pm.connectAttr(offsetz.output, axis.translateZ)
    
        maxis.append(axis)
        
    return pm.group(*maxis, n='RotationAnimation')   
    
""" Offsets & Orients """

def orients_global(anim):

    joints  = np.arange(anim.shape[1])
    parents = np.arange(anim.shape[1])
    locals  = anim.orients
    globals = Quaternions.id(anim.shape[1])
    
    globals[:,0] = locals[:,0]
    
    for i in range(1, anim.shape[1]):
        globals[:,i] = globals[:,anim.parents[i]] * locals[:,i]
        
    return globals

    
def offsets_transforms_local(anim):
    
    transforms = anim.orients[np.newaxis].transforms()
    transforms = np.concatenate([transforms, np.zeros(transforms.shape[:2] + (3, 1))], axis=-1)
    transforms = np.concatenate([transforms, np.zeros(transforms.shape[:2] + (1, 4))], axis=-2)
    transforms[:,:,0:3,3] = anim.offsets[np.newaxis]
    transforms[:,:,3:4,3] = 1.0
    return transforms
    
    
def offsets_transforms_global(anim):
    
    joints  = np.arange(anim.shape[1])
    parents = np.arange(anim.shape[1])
    locals  = offsets_transforms_local(anim)
    globals = transforms_blank(anim)

    globals[:,0] = locals[:,0]
    
    for i in range(1, anim.shape[1]):
        globals[:,i] = transforms_multiply(globals[:,anim.parents[i]], locals[:,i])
        
    return globals
    
def offsets_global(anim):
    offsets = offsets_transforms_global(anim)[:,:,:,3]
    return offsets[0,:,:3] / offsets[0,:,3,np.newaxis]
    
""" Lengths """

def offset_lengths(anim):
    return np.sum(anim.offsets[1:]**2.0, axis=1)**0.5
    
    
def position_lengths(anim):
    return np.sum(anim.positions[:,1:]**2.0, axis=2)**0.5
    
    
""" Skinning """

def skin(anim, rest, weights, mesh, maxjoints=4):
    
    full_transforms = transforms_multiply(
        transforms_global(anim), 
        transforms_inv(transforms_global(rest[0:1])))
    
    weightids = np.argsort(-weights, axis=1)[:,:maxjoints]
    weightvls = np.array(list(map(lambda w, i: w[i], weights, weightids)))
    weightvls = weightvls / weightvls.sum(axis=1)[...,np.newaxis]
    
    verts = np.hstack([mesh, np.ones((len(mesh), 1))])
    verts = verts[np.newaxis,:,np.newaxis,:,np.newaxis]
    verts = transforms_multiply(full_transforms[:,weightids], verts)    
    verts = (verts[:,:,:,:3] / verts[:,:,:,3:4])[:,:,:,:,0]

    return np.sum(weightvls[np.newaxis,:,:,np.newaxis] * verts, axis=2)
    



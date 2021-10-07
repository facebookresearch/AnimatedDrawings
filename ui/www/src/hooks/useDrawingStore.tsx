import create from "zustand";
import { Pose } from "../components/PoseEditor";
import { BoundingBox } from "../components/Canvas/CanvasBoundingBox";

type DrawingState = {
  drawing: string; // Base64
  newCompressedDrawing: File | any;
  originalDimension: any;
  uuid: string;
  croppedImgDimensions : any;
  pose: Pose;
  boundingBox: BoundingBox;
  videoDownload: string;
  animationType: AnimationType;
  imageUrlPose?: string; // Cropped Image
  imageUrlMask?: string; // Mask Image
  animationFiles: File[];
  setDrawing: (imported: any) => void;
  setNewCompressedDrawing: (file: File) => void;
  setOriginalDimensions: (data: any) => void;
  setUuid: (uuid: string) => void;
  setCroppedImgDimensions: (data: any) => void;
  setPose: (n_pose: Pose) => void;
  setBox: (dimensions: any) => void;
  setVideoDownload: (url: string) => void;
  setAnimationType: (ani_type: any) => void;
  setImageUrlPose: (url: string | any) => void;
  setImageUrlMask: (url: string | any) => void;
  setAnimationFiles: (files: File[]) => void;
};

enum AnimationType {
  RunJump = "running_jump",
  Wave = "wave_hello_3",
  Dance = "hip_hop_dancing",
  BoxJump = "box_jump",
  Boxing = "boxing",
  CatWalk = "catwalk_walk",
  DabDance = "dab_dance",
  Dance001 = "dance_001",
}

const useDrawingStore = create<DrawingState>((set) => ({
  drawing: "",
  newCompressedDrawing: null,
  originalDimension: { width: 10, height: 10 },
  uuid: "",
  croppedImgDimensions : { width: 0, height: 0 },
  pose: { nodes: [], edges: [] },
  boundingBox: { x: 200, width: 100, y: 200, height: 100, id: "1" },
  videoDownload: "",
  animationType: AnimationType.RunJump,
  imageUrlPose: undefined,
  imageUrlMask: undefined,
  animationFiles: [],
  setDrawing: (imported) => set(() => ({ drawing: imported })),
  setNewCompressedDrawing: (file) =>
    set(() => ({ newCompressedDrawing: file })),
  setOriginalDimensions: (data) => set(() => ({ originalDimension: data })),
  setUuid: (uuid) => set(() => ({ uuid: uuid })),
  setCroppedImgDimensions: (data) => set(() => ({ croppedImgDimensions: data })),
  setPose: (n_pose) => set(() => ({ pose: n_pose })),
  setBox: (newBB) => set(() => ({ boundingBox: newBB })),
  setVideoDownload: (url) => set(() => ({ videoDownload: url })),
  setAnimationType: (ani_type) => set(() => ({ animationType: ani_type })),
  setImageUrlPose: (url) => set(() => ({ imageUrlPose: url })),
  setImageUrlMask: (url) => set(() => ({ imageUrlMask: url })),
  setAnimationFiles: (files) => set(() => ({ animationFiles: files })),
}));

export default useDrawingStore;

import create from "zustand";
import { Pose } from "../components/PoseEditor";

type DrawingState = {
  drawing: string; // Base64
  newCompressedDrawing: File | any;
  uuid: string;
  pose: Pose;
  videoDownload: string;
  animationType: AnimationType;
  imageUrlPose?: string;  // Cropped Image
  imageUrlMask?: string;  // Mask Image
  animationFiles: File[];
  setDrawing: (imported: any) => void;
  setNewCompressedDrawing: (file: File) => void;
  setUuid: (uuid: string) => void;
  setPose: (n_pose: Pose) => void;
  setVideoDownload: (url: string) => void;
  setAnimationType: (ani_type: any) => void;
  setImageUrlPose: (url: string | any) => void;
  setImageUrlMask: (url: string | any) => void;
  setAnimationFiles: (files: File[]) => void;
};

enum AnimationType {
  RunJump = "run_jump",
  Wave = "wave",
  Dance = "dance",
  BoxJump = "box_jump",
  Boxing = "boxing",
  CatWalk = "catwalk_walk",
  DabDance = "dab_dance",
  Dance001 = "dance_001"
}

const useDrawingStore = create<DrawingState>((set) => ({
  drawing: "",
  newCompressedDrawing: null,
  uuid: "",
  pose: { nodes: [], edges: [] },
  videoDownload: "",
  animationType: AnimationType.RunJump,
  imageUrlPose: undefined,
  imageUrlMask: undefined,
  animationFiles: [],
  setDrawing: (imported) => set(() => ({ drawing: imported })),
  setNewCompressedDrawing: (file) =>
    set(() => ({ newCompressedDrawing: file })),
  setUuid: (uuid) => set(() => ({ uuid: uuid })),
  setPose: (n_pose) => set(() => ({ pose: n_pose })),
  setVideoDownload: (url) => set(() => ({ videoDownload: url })),
  setAnimationType: (ani_type) => set(() => ({ animationType: ani_type })),
  setImageUrlPose: (url) => set(() => ({imageUrlPose: url})),
  setImageUrlMask: (url) => set(() => ({imageUrlMask: url})),
  setAnimationFiles: (files) => set(() =>({animationFiles : files}))
}));

export default useDrawingStore;

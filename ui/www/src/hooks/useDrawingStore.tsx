import create from "zustand";
import { Pose } from "../components/PoseEditor";

type DrawingState = {
  drawing: string; //base64
  newCompressedDrawing: File | any;
  uuid: string;
  pose: Pose;
  videoDownload: string;
  animationType: AnimationType;
  animationFiles: File[];
  setDrawing: (imported: any) => void;
  setNewCompressedDrawing: (file: File) => void;
  setUuid: (uuid: string) => void;
  setPose: (n_pose: Pose) => void;
  setVideoDownload: (url: string) => void;
  setAnimationType: (ani_type: any) => void;
  setAnimationFiles: (files: File[]) => void;
};

enum AnimationType {
  RunJump = "run_jump",
  Wave = "wave",
  Dance = "dance",
}

const useDrawingStore = create<DrawingState>((set) => ({
  drawing: "",
  newCompressedDrawing: null,
  uuid: "",
  pose: { nodes: [], edges: [] },
  videoDownload: "",
  animationType: AnimationType.RunJump,
  animationFiles: [],
  setDrawing: (imported) => set(() => ({ drawing: imported })),
  setNewCompressedDrawing: (file) =>
    set(() => ({ newCompressedDrawing: file })),
  setUuid: (uuid) => set(() => ({ uuid: uuid })),
  setPose: (n_pose) => set(() => ({ pose: n_pose })),
  setVideoDownload: (url) => set(() => ({ videoDownload: url })),
  setAnimationType: (ani_type) => set(() => ({ animationType: ani_type })),
  setAnimationFiles: (files) => set(() =>({animationFiles : files}))
}));

export default useDrawingStore;

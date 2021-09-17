import create from "zustand";

interface Line {
  tool: string;
  penSize: number;
  points: Array<number>
}

type MaskingState = {
  tool: string;
  penSize: number;
  lines: Line[];
  editMode : boolean;
  maskBase64: string;
  setTool:(tool: string) => void;
  setPenSize: (penSize: any) => void;
  setLines: (lines: Line[] ) => void;
  setEditMode : (mode: boolean) => void;
  setMaskBase64 : (data: string) => void;
};

const useMaskingStore = create<MaskingState>((set) => ({
  tool: "eraser",
  penSize: 4,
  lines: [],
  editMode: true,
  maskBase64: "",
  setTool: (tool) => set(() => ({ tool: tool })),
  setPenSize: (number) => set(() => ({ penSize: number })),
  setLines: (newLines) => set(() => ({lines : newLines})),
  setEditMode: () => set(state => ({ editMode: !state.editMode })),
  setMaskBase64: (data) => set(() => ({ maskBase64 : data}))
}));

export default useMaskingStore;

import create from "zustand";

type StepperState = {
  agreeTerms: boolean | null;
  currentStep: number;
  setCurrentStep: (step: number) => void;
  setAgreeTerms: (agreed: boolean) => void;
};

const useStepperStore = create<StepperState>((set) => ({
  agreeTerms: null,
  currentStep: 1,
  setCurrentStep: (step) => set(() => ({ currentStep: step })),
  setAgreeTerms: (agreed) => set(() => ({ agreeTerms: agreed })),
}));

export default useStepperStore;

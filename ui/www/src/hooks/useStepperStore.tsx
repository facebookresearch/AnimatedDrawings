import create from "zustand";

type StepperState = {
  agreeTerms: boolean | null;
  currentStep: number;
  errorCode: number | string;
  setCurrentStep: (step: number) => void;
  setAgreeTerms: (agreed: boolean) => void;
  setError: (code: number | string) => void
};

const useStepperStore = create<StepperState>((set) => ({
  agreeTerms: null,
  currentStep: 1,
  errorCode: 0,
  setCurrentStep: (step) => set(() => ({ currentStep: step })),
  setAgreeTerms: (agreed) => set(() => ({ agreeTerms: agreed })),
  setError: (code) => set(() => ({ errorCode: code })),
}));

export default useStepperStore;

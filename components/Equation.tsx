import { MathJax } from "better-react-mathjax";

export default function Equation({ children, style }) {
  return (
    <div
      className="comp_equation flex w-full items-center justify-center"
      style={style}
    >
      <MathJax>{children}</MathJax>
    </div>
  );
}

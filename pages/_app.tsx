import "../styles/globals.css";
import { MathJaxContext } from "better-react-mathjax";

export default function App({ Component, pageProps }) {
  return (
    <MathJaxContext>
      <Component {...pageProps} />
    </MathJaxContext>
  );
}

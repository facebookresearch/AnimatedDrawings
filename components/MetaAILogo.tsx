import Link from "next/link";
import logo_white from "../public/assets/meta/metaai_logo_white.svg";
import logo_black from "../public/assets/meta/metaai_logo_black.svg";
import logo_positive from "../public/assets/meta/metaai_logo_positive.svg";
import logo_negative from "../public/assets/meta/metaai_logo_negative.svg";

export type MetaAILogoVariant = "white" | "black" | "positive" | "negative";
export type MetaAILogoProps = { className?:string, variant:MetaAILogoVariant, link?:boolean, style?:object };

export default function MetaAILogo({ className='', variant, link, style }:MetaAILogoProps) {

  const getLogo = (which) => {
    switch (which) {
      case "white":
        return logo_white;
      case "black":
        return logo_black;
      case "positive":
        return logo_positive;
      case "negative":
        return logo_negative;
      default:
        return logo_positive;
    }
  }

  const styles = {
    background: `url(${getLogo(variant).src}) no-repeat center center`,
    backgroundSize: "contain",
    ...style,
  }

  const logo = <div className={`block w-full h-full ${className} ${link ? 'cursor-pointer' : 'cursor-default'}`} style={styles}></div>;

  return (link ? <Link href="https://ai.facebook.com/">{logo}</Link> : logo);
}

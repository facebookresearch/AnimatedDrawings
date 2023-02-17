const Site = require("../site.json");
import Link from "next/link";
import { RiArrowRightUpLine } from "react-icons/ri";

export default function ActionButton({ url, children, color, small, openNew, style }) {
  const c = color || `${Site.theme}-${Site.shade + 100}`;
  const size = small ? "px-3 py-2 text-sm" : "px-6 py-4 text-md";
  const classes = `flex rounded-md no-underline items-center justify-center font-semibold text-white hover:text-${c} hover:shadow-md bg-${c} hover:bg-white ${size} ${openNew ? 'gap-1 pr-2' : ''}`;

  return (
    <span className="comp_button inline-block" style={style}>
      {!openNew && <Link href={url} passHref><a className={classes}>{children}</a></Link>}
      {openNew && <a href={url} target="_blank" rel="noopener" className={classes}>{children} <RiArrowRightUpLine /></a>}
    </span>
  );
}

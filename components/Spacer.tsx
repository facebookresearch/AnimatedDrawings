export type SpacerProps = {
  size?: "3xs" | "2xs" | "xs" | "sm" | "md" | "lg" | "xl" | "2xl" | "3xl";
}

export function Spacer({
  size="xs"
}) {
  const sizes = {
    "3xs": "h-[0.5rem]",
    "2xs": "h-[1rem]",
    "xs": "h-[1.5rem]",
    "sm": "h-[2rem]",
    "md": "h-[2.5rem]",
    "lg": "h-[3.5rem]",
    "xl": "h-[5rem]",
    "2xl": "h-[7.5rem]", 
    "3xl": "h-[10rem]"
  }
  return (
    <div className={`w-full ${sizes[size] || sizes.xs}`}></div>
  )
}
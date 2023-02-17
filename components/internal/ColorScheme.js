const colors = [
  "gray",
  "blue",
  "pink",
  "purple",
  "teal",
  "green",
  "yellow",
  "cyan",
  "orange",
  "red",
];
const scales = [
  "50",
  "100",
  "200",
  "300",
  "400",
  "500",
  "600",
  "700",
  "800",
  "900",
];

export function ColorScheme() {
  return (
    <>
      {colors.map((c) => (
        <div key={c}>
          <ColorRow name={c} />
        </div>
      ))}
    </>
  );
}

export function ColorRow({ name }) {
  return (
    <>
      {scales.map((s) => (
        <span
          key={name + s}
          className={`bg-${name}-${s} ${
            parseInt(s) < 400 ? "text-slate-500" : "text-white"
          } block p-1 m-[1px] text-[9px] md:w-[8%] w-[7vw] inline-block md:p-1`}
        >
          {name}
          <br />
          {s}
        </span>
      ))}
    </>
  );
}

export function ColorThemeBlock({ one, two, three, name }) {
  return (
    <div>
      <div className="mt-5 mb-1 text-sm text-slate-600">{name}</div>
      <div className="flex flex-row">
        <div
          className={`flex flex-1 flex-grow-3 items-center justify-center bg-${one} text-white box-border p-10`}
        >
          {one}
        </div>
        <div
          className={`flex flex-1 items-center justify-center bg-${two} text-white py-10`}
        >
          {two}
        </div>
        <div
          className={`flex flex-1 items-center justify-center bg-${three} text-slate-900 py-10`}
        >
          {three}
        </div>
      </div>
    </div>
  );
}

const { inherit } = require("tailwindcss/colors");

const defaultColors = {
  "gray": {
    50: "#f1f4f7",
    100: "#DEE3E9",
    200: "#CBD2D9",
    300: "#A7B3BF",
    400: "#8595A4",
    500: "#667788",
    600: "#465A69",
    700: "#344854",
    800: "#1C2B33",
    900: "#0F191E",
  },
  "blue": {
    50: "#E8F3FF",
    100: "#CCE6FF",
    200: "#AFD7FF",
    300: "#84BCF5",
    400: "#61A3F3",
    500: "#3880F3",
    600: "#2962D9",
    700: "#1D4AB2",
    800: "#081D6A",
    900: "#020A4D",
  },
  "pink": {
    50: "#FFF0FA",
    100: "#FFE1F5",
    200: "#FFD2F0",
    300: "#FAB9E6",
    400: "#FA9BD7",
    500: "#FA7DC8",
    600: "#D75FAA",
    700: "#B43C8C",
    800: "#640055",
    900: "#41002D",
  },
  "purple": {
    50: "#EEEDFD",
    100: "#E1E1FF",
    200: "#D2D2FF",
    300: "#B9B4FF",
    400: "#A096FF",
    500: "#8773FF",
    600: "#6E55E1",
    700: "#6441D2",
    800: "#280578",
    900: "#0A005A",
  },
  "teal": {
    50: "#DCFAF7",
    100: "#C3F5F0",
    200: "#A5F0E6",
    300: "#6EE6D2",
    400: "#3CE1C8",
    500: "#00D2BE",
    600: "#009B9B",
    700: "#00787D",
    800: "#00414B",
    900: "#00232D",
  },
  "green": {
    50: "#E6FDEB",
    100: "#CDFAC3",
    200: "#B9F5AA",
    300: "#8CE669",
    400: "#6EE146",
    500: "#28D232",
    600: "#0F9B14",
    700: "#007D1E",
    800: "#003728",
    900: "#002514",
  },
  "yellow": {
    50: "#FDFDDC",
    100: "#FFFAC3",
    200: "#FFF3AD",
    300: "#FFE87A",
    400: "#FFDC32",
    500: "#F0AA19",
    600: "#D2780A",
    700: "#AF5A00",
    800: "#501E00",
    900: "#371900",
  },
  "cyan": {
    50: "#DCFAFF",
    100: "#BEF5FC",
    200: "#A5F0FA",
    300: "#6EE6F5",
    400: "#3CD7F5",
    500: "#00C8F0",
    600: "#0096C8",
    700: "#0073AA",
    800: "#00375F",
    900: "#001E46",
  },
  "orange": {
    50: "#FFF5EB",
    100: "#FFE9D2",
    200: "#FFDCB9",
    300: "#FABE82",
    400: "#FAA550",
    500: "#FA8719",
    600: "#DC6414",
    700: "#A0460A",
    800: "#5A1900",
    900: "#410F00",
  },
  "red": {
    50: "#FFEEF0",
    100: "#FFD6D9",
    200: "#FFB1B7",
    300: "#FA8791",
    400: "#F05F69",
    500: "#E6193B",
    600: "#C80A28",
    700: "#AA0A1E",
    800: "#5A0000",
    900: "#460000",
  },

}


// We are adding all color classes to safeList
const colors = [
  "slate",
  "gray",
  "zinc",
  "neutral",
  "stone",
  "red",
  "orange",
  "amber",
  "yellow",
  "lime",
  "green",
  "emerald",
  "teal",
  "cyan",
  "sky",
  "blue",
  "indigo",
  "violet",
  "purple",
  "fuchsia",
  "pink",
  "rose",
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
const types = ["bg", "border", "text"];

// States like hover and focus (see https://tailwindcss.com/docs/hover-focus-and-other-states)
// Add to this list as needed
const states = ["hover"];

const colorSafeList = [];
for (let i = 0; i < types.length; i++) {
  const t = types[i];

  for (let j = 0; j < colors.length; j++) {
    const c = colors[j];

    for (let k = 0; k < scales.length; k++) {
      const s = scales[k];

      colorSafeList.push(`${t}-${c}-${s}`);

      for (let l = 0; l < states.length; l++) {
        const st = states[l];
        colorSafeList.push(`${st}:${t}-${c}-${s}`);
      }
    }
  }
}

// console.log(colorSafeList);

module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./sections/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    fontSize: {
      xs: ["0.75rem", { lineHeight: "1.5" }],
      sm: ["0.875rem", { lineHeight: "1.5" }],
      base: ["1rem", { lineHeight: "1.5" }],
      lg: ["1.125rem", { lineHeight: "1.2", fontWeight: 500 }],
      xl: ["1.25rem", { lineHeight: "1.2", fontWeight: 500 }],
      "2xl": ["1.5rem", { lineHeight: "1.2", fontWeight: 500, letterSpacing: "0.005rem" }],
      "3xl": ["2.25rem", { lineHeight: "1.2", fontWeight: 500, letterSpacing: "0.01rem" }],
      "4xl": ["3rem", { lineHeight: "1.2", fontWeight: 500, letterSpacing: "0.016rem" }],
      "5xl": ["4rem", { lineHeight: "1.2", fontWeight: 400, letterSpacing: "0.016rem" }],
      "6xl": ["5rem", { lineHeight: "1.2", fontWeight: 400, letterSpacing: "0.016rem" }],
    },
    extend: {
      colors: defaultColors,
      lineHeight: {
        "tight": 1.2,
      },
      typography: (theme) => ({
        starter: {
          /* prose-starter */
          css: {
            strong: { color: "inherit" },
            ".color-flip": {
              a: {
                color: "#fff",
              },
              code: {
                color: "#fff",
              },
            }
          },
        },
      }),
    },
  },
  corePlugins: {
    aspectRatio: false,
  },
  plugins: [
    require("daisyui"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/aspect-ratio"),
  ],

  daisyui: {
    styled: true,
    themes: [
      {
        light: {
          ...require("daisyui/src/colors/themes")["[data-theme=light]"],
          primary: "#0064E0",
          "primary-content": "#FFFFFF",
          secondary: "#1C2B33",
          "secondary-content": "#FFFFFF",
          accent: "#6441D2",
          "accent-content": "#FFFFFF",
          info: "#009B9B",
          "info-content": "#FFFFFF",
          success: "#0F9B14",
          "success-content": "#FFFFFF",
          warning: "#FA8719",
          "warning-content": "#FFFFFF",
          error: "#C80A28",
          "error-content": "#FFFFFF",
        },
      }
    ],
  },
  safelist: [].concat(colorSafeList),
};

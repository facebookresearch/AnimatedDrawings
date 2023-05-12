import { Application } from "pixi.js";
import { Scene } from "./scenes/scene"; // This is the import statement

const app = new Application({
  view: document.getElementById("pixi-canvas") as HTMLCanvasElement,
  resolution: window.devicePixelRatio || 1,
  autoDensity: true,
  backgroundColor: 0x6495ed,
  width: 1400,
  height: 1000,
});

// pass in the screen size to avoid "asking up"
const sceny: Scene = new Scene(app.screen.width, app.screen.height);

app.stage.addChild(sceny);

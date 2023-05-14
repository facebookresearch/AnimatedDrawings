import { Container, Text } from "pixi.js";

export class DebugMsg extends Container {
  private text: Text = new Text("FPS: 0");
  private lastTime: number = performance.now();
  private frameCount: number = 0;

  constructor() {
    super();
    this.text.x = 10;
    this.text.y = 10;
    this.text.style = {
      fontFamily: "Arial",
      fontSize: 24,
      fill: "blue",
    };
    this.addChild(this.text);
    this.zIndex = 1000;
  }

  public update(_: number): void {
    const now = performance.now();
    const deltaTime = (now - this.lastTime) / 1000;
    this.frameCount++;
    if (deltaTime >= 1) {
      this.text.text = `FPS: ${this.frameCount}`;
      this.frameCount = 0;
      this.lastTime = now;
    }
  }
}

import { Container, Sprite } from "pixi.js";

export class Background extends Container {
  private background: Sprite = new Sprite();

  constructor(screenWidth: number, screenHeight: number) {
    super();
    this.initialize(screenWidth, screenHeight);
  }

  private async initialize(width: number, height: number): Promise<void> {
    this.background = Sprite.from("background.png");
    this.background.anchor.set(0.5);
    this.background.scale.set(1);
    this.background.x = width / 2;
    this.background.y = height / 2;
    this.addChild(this.background);
    this.zIndex = 1;
  }
}

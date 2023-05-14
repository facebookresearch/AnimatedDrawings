import { Container, Sprite, Assets } from "pixi.js";
import "@pixi/gif";

export class CharacterCircle extends Container {
  private character: Sprite = new Sprite();
  private readonly ellipse_ratio = 0.75;
  private readonly depth_size_ratio = 0.9;
  public speed = 1;
  public degree = 0;
  public radius = 100;
  public center = { x: 500, y: 500 };

  constructor(image: string) {
    super();
    this.initialize(image);
  }

  private async initialize(image: string): Promise<void> {
    this.character = await Assets.load(image);
    this.character.anchor.set(0.5);
    this.character.scale.set(1);
    this.addChild(this.character);
    this.zIndex = 10;
    console.log(image);
  }

  public pos(): { x: number; y: number } {
    return { x: this.character.x, y: this.character.y };
  }

  public update(deltaTime: number): void {
    this.degree += this.speed * deltaTime;
    this.x =
      this.radius * Math.cos((this.degree * Math.PI) / 180) + this.center.x;
    this.y =
      this.ellipse_ratio *
        this.radius *
        Math.sin((this.degree * Math.PI) / 180) +
      this.center.y;

    // 位置によってスケールを変える
    this.character.scale.set(
      (this.depth_size_ratio * (this.y - this.center.y)) / this.center.y + 1
    );
  }
}

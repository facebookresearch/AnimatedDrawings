import { Container, Sprite, Assets } from "pixi.js";
import "@pixi/gif";

export class Character extends Container {
  private character: Sprite = new Sprite();
  private dx: number = 500;
  private dy: number = 500;
  private boundaryLeft: number = 0;
  private boundaryRight: number = 1000;
  private boundaryTop: number = 0;
  private boundaryBottom: number = 1000;

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

  public setPos(x: number, y: number): void {
    this.character.x = x;
    this.character.y = y;
  }

  public pos(): { x: number; y: number } {
    return { x: this.character.x, y: this.character.y };
  }

  public setVelocity(dx: number, dy: number): void {
    this.dx = dx;
    this.dy = dy;
  }

  // TODO: 本来は定義されたパターンを設定する
  public setPattern(left: number, right: number, top: number, bottom: number) {
    this.boundaryLeft = left;
    this.boundaryRight = right;
    this.boundaryTop = top;
    this.boundaryBottom = bottom;
  }

  public update(deltaTime: number): void {
    this.character.x += this.dx * deltaTime;
    this.character.y += this.dy * deltaTime;
    if (
      this.character.x < this.boundaryLeft ||
      this.character.x > this.boundaryRight
    ) {
      this.dx *= -1;
    }
    if (
      this.character.y < this.boundaryTop ||
      this.character.y > this.boundaryBottom
    ) {
      this.dy *= -1;
    }
  }
}

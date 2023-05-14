import { Container, Sprite, Assets } from "pixi.js";
import "@pixi/gif";

export class Character extends Container {
  private character: Sprite = new Sprite();
  private dx: number = 500;
  private dy: number = 500;
  private boundary_left: number = 0;
  private boundary_right: number = 1000;
  private boundary_top: number = 0;
  private boundary_bottom: number = 1000;

  constructor(imagePath: string, loadedImage?: Sprite) {
    super();
    this.initialize(imagePath, loadedImage);
  }

  private async initialize(
    imagePath: string,
    loadedImage?: Sprite
  ): Promise<void> {
    this.character = loadedImage ? loadedImage : await Assets.load(imagePath);
    this.character.anchor.set(0.5);
    this.character.scale.set(1);
    this.addChild(this.character);
    console.log(imagePath);
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
    this.boundary_left = left;
    this.boundary_right = right;
    this.boundary_top = top;
    this.boundary_bottom = bottom;
  }

  public update(deltaTime: number): void {
    this.character.x += this.dx * deltaTime;
    this.character.y += this.dy * deltaTime;
    if (
      this.character.x < this.boundary_left ||
      this.character.x > this.boundary_right
    ) {
      this.dx *= -1;
    }
    if (
      this.character.y < this.boundary_top ||
      this.character.y > this.boundary_bottom
    ) {
      this.dy *= -1;
    }
  }
}

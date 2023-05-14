import { Container, Ticker } from "pixi.js";
import { Character } from "./Character";
import { CharacterCircle } from "./CharacterCircle";
import { Firework } from "./Firework";
import { DebugMsg } from "./DebugMsg";
import { generator } from "../utility/generator";
import { loader } from "../utility/loader";

export class Scene extends Container {
  private readonly screenWidth: number;
  private readonly screenHeight: number;
  private readonly numCharacters: number = 5;
  private readonly speed: number = 0.5;

  private characters: Character[] = [];
  private characterCircles: CharacterCircle[] = [];
  private firework: Firework = new Firework(this);
  private debugText: DebugMsg = new DebugMsg();
  constructor(screenWidth: number, screenHeight: number) {
    super();
    this.screenWidth = screenWidth;
    this.screenHeight = screenHeight;
    this.initialize();
  }

  private async initialize(): Promise<void> {
    // character
    for (let i = 1; i <= this.numCharacters; i++) {
      const chara = new Character(`woman${i}.gif`);
      chara.setPos(5 * i + (250 + (i % 10) * 100), 5 * i + 400);
      chara.setVelocity(
        Math.random() * 2 * this.speed - this.speed,
        Math.random() * 2 * this.speed - this.speed
      );
      chara.setPattern(0, this.screenWidth, 0, this.screenHeight);
      this.characters.push(chara);
      this.addChild(chara);
    }

    // character
    for (let i = 1; i <= 10; i++) {
      const chara = new CharacterCircle(`garlic${i}.gif`);
      chara.radius = Math.random() * 200 + 200;
      chara.degree = Math.random() * 360;
      chara.speed = Math.random() * 0.2;
      this.characterCircles.push(chara);
      this.addChild(chara);
    }

    await loader();

    // characters from s3
    const chars = generator().map((c, i) => {
      c.setPos(5 * i + (250 + (i % 10) * 100), 5 * i + 400);
      c.setVelocity(
        Math.random() * 2 * this.speed - this.speed,
        Math.random() * 2 * this.speed - this.speed
      );
      c.setPattern(0, this.screenWidth, 0, this.screenHeight);
      this.addChild(c);
      return c;
    });
    this.characters = this.characters.concat(chars);

    // debug
    this.addChild(this.debugText);

    Ticker.shared.add(this.update, this);
    this.addChild;
  }

  private update(deltaTime: number): void {
    this.characters.forEach((chara) => {
      chara.update(deltaTime);
    });
    this.characterCircles.forEach((chara) => {
      chara.update(deltaTime);
    });
    this.firework.update(deltaTime);
    this.debugText.update(deltaTime);
  }
}

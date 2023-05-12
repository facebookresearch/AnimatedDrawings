import { sound } from "@pixi/sound";

export class Sounds {
  constructor() {
    const a = sound.add("bgm", "../bonodori.mp3");
    console.log(a);
    sound.add("se-firework", "../firework.mp3");
  }

  public playBgm(): void {
    sound.play("bgm", { loop: true });
    console.log(sound.isPlaying());
  }

  public pauseBgm(): void {
    sound.pause("bgm");
  }

  public playFirework(): void {
    sound.play("se-firework");
  }
}

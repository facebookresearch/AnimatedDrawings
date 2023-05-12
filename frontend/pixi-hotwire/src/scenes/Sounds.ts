import { sound } from "@pixi/sound";

export class Sounds {
  public static initialize() {
    const a = sound.add("bgm", "../bonodori.mp3");
    console.log(a);
    sound.add("se-firework", "../firework.mp3");
  }

  public static playBgm(): void {
    sound.play("bgm", { loop: true });
    console.log(sound.isPlaying());
  }

  public static pauseBgm(): void {
    sound.pause("bgm");
  }

  public static isPlaying(): boolean {
    return sound.isPlaying();
  }

  public static playFirework(): void {
    sound.play("se-firework");
  }
}

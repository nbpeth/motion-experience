import { starfieldConfig } from "./starfield.config.js";

async function start() {
  await loadSlim(tsParticles);
  await tsParticles.load({ id: "starfield", options: starfieldConfig });
}

start().catch((error) => console.error("Failed to start starfield:", error));

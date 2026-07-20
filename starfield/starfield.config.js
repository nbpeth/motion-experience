export function starfieldConfig(n) {
  return {
    fpsLimit: 60,
    detectRetina: true,
    interactivity: {
      detectsOn: "window",
      events: {
        onscroll: {

        },
        onHover: {
          enable: true,
          mode: "repulse",
        },
      },
      modes: {
        repulse: {
          distance: 200,
          duration: 1,
          speed: 1,
        },
      },
    },
    particles: {
      life: {
        count: Infinity,
        duration: {
          value: {
            min: 15,
            max: 50,
          },
        },
      },
      number: {
        value: n * 10,
        density: {
          enable: true,
        },
      },
      color: {
        value: ["#ffffff", "#bfd7ff", "#fff4d6"],
      },
      shape: {
        type: "circle",
      },
      size: {
        value: { min: 0.4, max: 5 },
      },
      opacity: {
        value: { min: 0.1, max: 0.9 },
        animation: {
          enable: true,
          speed: 0.6,
          sync: false,
        },
      },
      move: {
        enable: true,
        speed: { min: 0.05, max: 0.3 },
        direction: "none",
        random: true,
        straight: false,
      },
    },
  };
}

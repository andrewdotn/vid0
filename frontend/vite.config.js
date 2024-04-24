export default {
  build: {
    // add an extra level of nesting so that collectstatic will gather
    // built frontend files into a `dist` directory, avoiding collisions
    outDir: "static/dist",
  },
};

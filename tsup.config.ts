import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts", "src/bin.ts"],
  format: ["esm"],
  target: "node20",
  dts: { entry: { index: "src/index.ts" } },
  clean: true,
  sourcemap: true,
});

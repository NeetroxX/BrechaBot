#!/usr/bin/env node
// Executable entry for the `brechabot` bin. Always runs — no entry guard,
// so it works through npm's global shim regardless of argv[1]/path resolution.
import { main } from "./cli.js";

main();

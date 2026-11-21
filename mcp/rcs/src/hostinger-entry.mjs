// SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
// SPDX-License-Identifier: MIT OR Apache-2.0
//
// Hostinger imports the entry module using its own process runner;
// process.argv[1] is NOT this module. Start the listener upon import.
// The reusable Node transport retains its side-effect-free import behavior.
import { startNodeServer } from "./node.mjs";

startNodeServer();

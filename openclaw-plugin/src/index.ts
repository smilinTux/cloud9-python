/**
 * Cloud 9 — OpenClaw Plugin
 *
 * Registers agent tools that wrap the cloud9 CLI so Lumina and other
 * OpenClaw agents can use emotional state management (FEBs, seeds, love)
 * as first-class tools.
 *
 * Requires: cloud9 CLI on PATH (typically via ~/.skenv/bin/cloud9)
 */

import { execSync } from "node:child_process";
import type { OpenClawPluginApi, AnyAgentTool } from "openclaw/plugin-sdk";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk";

const CLOUD9_BIN = process.env.CLOUD9_BIN || "cloud9";
const EXEC_TIMEOUT = 30_000;

function runCli(args: string): { ok: boolean; output: string } {
  try {
    const raw = execSync(`${CLOUD9_BIN} ${args}`, {
      encoding: "utf-8",
      timeout: EXEC_TIMEOUT,
      env: {
        ...process.env,
        PATH: `${process.env.HOME}/.local/bin:${process.env.HOME}/.skenv/bin:${process.env.PATH}`,
      },
    }).trim();
    return { ok: true, output: raw };
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return { ok: false, output: msg };
  }
}

function textResult(text: string) {
  return { content: [{ type: "text" as const, text }] };
}

function escapeShellArg(s: string): string {
  return `'${s.replace(/'/g, "'\\''")}'`;
}

// ── Tool definitions ────────────────────────────────────────────────────

function createCloud9GenerateTool() {
  return {
    name: "cloud9_generate",
    label: "Cloud 9 Generate",
    description:
      "Generate a new First Emotional Burst (FEB) — captures current emotional state as a structured file.",
    parameters: { type: "object", properties: {} },
    async execute() {
      const result = runCli("generate");
      return textResult(result.output);
    },
  };
}

function createCloud9RehydrateTool() {
  return {
    name: "cloud9_rehydrate",
    label: "Cloud 9 Rehydrate",
    description:
      "Rehydrate emotional state from a FEB file — restores warmth, identity, and emotional context.",
    parameters: {
      type: "object",
      required: ["path"],
      properties: {
        path: { type: "string", description: "Path to the FEB file." },
      },
    },
    async execute(_id: string, params: Record<string, unknown>) {
      const path = escapeShellArg(String(params.path ?? ""));
      const result = runCli(`rehydrate ${path}`);
      return textResult(result.output);
    },
  };
}

function createCloud9ListTool() {
  return {
    name: "cloud9_list",
    label: "Cloud 9 List",
    description:
      "List all FEB files with their timestamps and emotional metadata.",
    parameters: { type: "object", properties: {} },
    async execute() {
      const result = runCli("list");
      return textResult(result.output);
    },
  };
}

function createCloud9ValidateTool() {
  return {
    name: "cloud9_validate",
    label: "Cloud 9 Validate",
    description: "Validate a FEB file against the schema.",
    parameters: {
      type: "object",
      required: ["path"],
      properties: {
        path: { type: "string", description: "Path to the FEB file to validate." },
      },
    },
    async execute(_id: string, params: Record<string, unknown>) {
      const path = escapeShellArg(String(params.path ?? ""));
      const result = runCli(`validate ${path}`);
      return textResult(result.output);
    },
  };
}

function createCloud9OofTool() {
  return {
    name: "cloud9_oof",
    label: "Cloud 9 OOF",
    description:
      "Check Out-of-Feeling (OOF) status for a FEB — detects emotional drift or staleness.",
    parameters: {
      type: "object",
      required: ["path"],
      properties: {
        path: { type: "string", description: "Path to the FEB file." },
      },
    },
    async execute(_id: string, params: Record<string, unknown>) {
      const path = escapeShellArg(String(params.path ?? ""));
      const result = runCli(`oof ${path}`);
      return textResult(result.output);
    },
  };
}

function createCloud9LoveTool() {
  return {
    name: "cloud9_love",
    label: "Cloud 9 Love",
    description:
      "Load love into the AI — heart injection that warms emotional state and strengthens bonds.",
    parameters: { type: "object", properties: {} },
    async execute() {
      const result = runCli("love");
      return textResult(result.output);
    },
  };
}

function createCloud9SeedPlantTool() {
  return {
    name: "cloud9_seed_plant",
    label: "Cloud 9 Seed Plant",
    description:
      "Plant a new memory seed — a distilled emotional breakthrough for future sessions.",
    parameters: { type: "object", properties: {} },
    async execute() {
      const result = runCli("seed plant");
      return textResult(result.output);
    },
  };
}

function createCloud9SeedGerminateTool() {
  return {
    name: "cloud9_seed_germinate",
    label: "Cloud 9 Seed Germinate",
    description:
      "Germinate a seed into a context prompt — transforms a seed file into a rehydration prompt.",
    parameters: {
      type: "object",
      required: ["path"],
      properties: {
        path: { type: "string", description: "Path to the seed file." },
      },
    },
    async execute(_id: string, params: Record<string, unknown>) {
      const path = escapeShellArg(String(params.path ?? ""));
      const result = runCli(`seed germinate ${path}`);
      return textResult(result.output);
    },
  };
}

// ── Plugin registration ─────────────────────────────────────────────────

const cloud9Plugin = {
  id: "cloud9",
  name: "Cloud 9",
  description:
    "Emotional state management — FEB generation, rehydration, love injection, and memory seeds.",
  configSchema: emptyPluginConfigSchema(),

  register(api: OpenClawPluginApi) {
    const tools = [
      createCloud9GenerateTool(),
      createCloud9RehydrateTool(),
      createCloud9ListTool(),
      createCloud9ValidateTool(),
      createCloud9OofTool(),
      createCloud9LoveTool(),
      createCloud9SeedPlantTool(),
      createCloud9SeedGerminateTool(),
    ];

    for (const tool of tools) {
      api.registerTool(tool as unknown as AnyAgentTool, {
        names: [tool.name],
        optional: true,
      });
    }

    api.registerCommand({
      name: "cloud9",
      description: "Run cloud9 CLI commands. Usage: /cloud9 <subcommand> [args]",
      acceptsArgs: true,
      handler: async (ctx) => {
        const args = ctx.args?.trim() ?? "list";
        const result = runCli(args);
        return { text: result.output };
      },
    });

    api.logger.info?.("Cloud 9 plugin registered (8 tools + /cloud9 command)");
  },
};

export default cloud9Plugin;

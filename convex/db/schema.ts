import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

const BestOf = v.union(v.literal(1), v.literal(3), v.literal(5));

defineSchema({
  users: defineTable({
    discordId: v.string(),
    username: v.string(),
    updateTime: v.number(),
  }),
  maps: defineTable({
    name: v.string(),
    isEnabled: v.boolean(),
    updateTime: v.number(),
  }),
  teams: defineTable({
    name: v.string(),
    captainId: v.id("users"),
    hasFirstPick: v.boolean(),
    threadId: v.optional(v.string()),
    voiceChannelId: v.optional(v.string()),
    updateTime: v.number(),
  }),
  players: defineTable({
    teamId: v.id("teams"),
    userId: v.id("users"),
    updateTime: v.number(),
  }),
  matches: defineTable({
    team1: v.id("teams"),
    team2: v.id("teams"),
    bestOf: BestOf,
    threadId: v.optional(v.string()),
    status: v.union(
      v.literal("veto_phase"),
      v.literal("in_progress"),
      v.literal("finished"),
    ),
    team1Score: v.optional(v.number()),
    team2Score: v.optional(v.number()),
    updateTime: v.number(),
  }),
  vetos: defineTable({
    matchId: v.id("matches"),
    action: v.union(
      v.literal("ban"),
      v.literal("pick"),
      v.literal("side_pick"),
      v.literal("decider"),
    ),
    order: v.number(),
    updateTime: v.number(),
  }),
  mapSelections: defineTable({
    vetoId: v.id("vetos"),
    mapId: v.id("maps"),
    updateTime: v.number(),
  }),
  sideSelections: defineTable({
    vetoId: v.id("vetos"),
    side: v.union(v.literal("ATK"), v.literal("DEF")),
    updateTime: v.number(),
  }),
  games: defineTable({
    matchId: v.number(),
    team1: v.number(),
    team2: v.number(),
    order: v.number(),
    updateTime: v.number(),
  }),
  mmr: defineTable({
    matchId: v.id("matches"),
    delta: v.number(),
    updateTime: v.number(),
  }),
});

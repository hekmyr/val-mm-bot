import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

const BestOf = v.union(v.literal(1), v.literal(3), v.literal(5));

defineSchema({
  users: defineTable({
    discordId: v.string(),
    username: v.string(),
    updateTime: v.number()
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
    updateTime: v.number()
  }),
  players: defineTable({
    teamId: v.id("teams"),
    userId: v.id("users"),
    updateTime: v.number()
  }),
  matches: defineTable({
    team1: v.id("teams"),
    team2: v.id("teams"),
    bestOf: BestOf,
    status: v.union(v.literal("ready_check"), v.literal("finished")),
    updateTime: v.number()
  }),
  vetos: defineTable({
    teamId: v.id("teams"),
    mapId: v.id("maps"),
    action: v.union(v.literal("ban"), v.literal("pick")),
    order: v.number(),
    updateTime: v.number()
  }),
  games: defineTable({
    vetoId: v.id("vetos"),
    team1: v.number(),
    team2: v.number(),
    updateTime: v.number()
  }),
  mmr: defineTable({
    matchId: v.id("matches"),
    delta: v.number(),
    updateTime: v.number()
  })
})
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const findById = query({
  args: { matchId: v.id("matches") },
  async handler(ctx, args) {
    return await ctx.db.get(args.matchId);
  },
});

export const findByThreadId = query({
  args: { threadId: v.string() },
  async handler(ctx, args) {
    return await ctx.db
      .query("matches")
      .filter((q) => q.eq(q.field("threadId"), args.threadId))
      .first();
  },
});

export const create = mutation({
  args: {
    team1: v.id("teams"),
    team2: v.id("teams"),
    bestOf: v.union(v.literal(1), v.literal(3), v.literal(5)),
    status: v.string(),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    const matchId = await ctx.db.insert("matches", {
      team1: args.team1,
      team2: args.team2,
      bestOf: args.bestOf,
      status: args.status as "veto_phase" | "in_progress" | "finished" | "archived",
      updateTime: args.updateTime,
    });

    return matchId;
  },
});

export const updateThreadId = mutation({
  args: {
    matchId: v.id("matches"),
    threadId: v.string(),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    await ctx.db.patch(args.matchId, {
      threadId: args.threadId,
      updateTime: args.updateTime,
    });
  },
});

export const updateStatus = mutation({
  args: {
    matchId: v.id("matches"),
    status: v.string(),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    await ctx.db.patch(args.matchId, {
      status: args.status as "veto_phase" | "in_progress" | "finished" | "archived",
      updateTime: args.updateTime,
    });
  },
});

export const setScore = mutation({
  args: {
    matchId: v.id("matches"),
    team1Score: v.number(),
    team2Score: v.number(),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    await ctx.db.patch(args.matchId, {
      team1Score: args.team1Score,
      team2Score: args.team2Score,
      status: "finished",
      updateTime: args.updateTime,
    });
  },
});

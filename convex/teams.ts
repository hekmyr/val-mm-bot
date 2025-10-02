import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const findById = query({
  args: { teamId: v.id("teams") },
  async handler(ctx, args) {
    return await ctx.db.get(args.teamId);
  },
});

export const findByThreadId = query({
  args: { threadId: v.string() },
  async handler(ctx, args) {
    return await ctx.db
      .query("teams")
      .filter((q) => q.eq(q.field("threadId"), args.threadId))
      .first();
  },
});

export const create = mutation({
  args: {
    name: v.string(),
    captainId: v.id("users"),
    hasFirstPick: v.boolean(),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    const teamId = await ctx.db.insert("teams", {
      name: args.name,
      captainId: args.captainId,
      hasFirstPick: args.hasFirstPick,
      updateTime: args.updateTime,
    });

    return teamId;
  },
});

export const updateThreadId = mutation({
  args: {
    teamId: v.id("teams"),
    threadId: v.string(),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    await ctx.db.patch(args.teamId, {
      threadId: args.threadId,
      updateTime: args.updateTime,
    });
  },
});

export const updateVoiceChannelId = mutation({
  args: {
    teamId: v.id("teams"),
    voiceChannelId: v.string(),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    await ctx.db.patch(args.teamId, {
      voiceChannelId: args.voiceChannelId,
      updateTime: args.updateTime,
    });
  },
});

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const findById = query({
  args: { userId: v.id("users") },
  async handler(ctx, args) {
    return await ctx.db.get(args.userId);
  },
});

export const findByDiscordId = query({
  args: { discordId: v.string() },
  async handler(ctx, args) {
    return await ctx.db
      .query("users")
      .filter((q) => q.eq(q.field("discordId"), args.discordId))
      .first();
  },
});

export const createOrFind = mutation({
  args: {
    discordId: v.string(),
    username: v.string(),
  },
  async handler(ctx, args) {
    const existing = await ctx.db
      .query("users")
      .filter((q) => q.eq(q.field("discordId"), args.discordId))
      .first();

    if (existing) {
      return existing._id;
    }

    const newUserId = await ctx.db.insert("users", {
      discordId: args.discordId,
      username: args.username,
      updateTime: Date.now(),
    });

    return newUserId;
  },
});

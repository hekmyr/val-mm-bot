import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: {
    teamId: v.id("teams"),
    userId: v.id("users"),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    const playerId = await ctx.db.insert("players", {
      teamId: args.teamId,
      userId: args.userId,
      updateTime: args.updateTime,
    });

    return playerId;
  },
});

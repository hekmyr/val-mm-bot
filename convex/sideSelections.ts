import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: {
    vetoId: v.id("vetos"),
    side: v.union(v.literal("ATK"), v.literal("DEF")),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    const selectionId = await ctx.db.insert("sideSelections", {
      vetoId: args.vetoId,
      side: args.side,
      updateTime: args.updateTime,
    });

    return selectionId;
  },
});

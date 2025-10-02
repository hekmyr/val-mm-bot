import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: {
    vetoId: v.id("vetos"),
    mapId: v.id("maps"),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    const selectionId = await ctx.db.insert("mapSelections", {
      vetoId: args.vetoId,
      mapId: args.mapId,
      updateTime: args.updateTime,
    });

    return selectionId;
  },
});

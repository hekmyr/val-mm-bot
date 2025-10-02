import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: {
    matchId: v.id("matches"),
    teamId: v.id("teams"),
    action: v.union(v.literal("ban"), v.literal("pick"), v.literal("side_pick"), v.literal("decider")),
    order: v.number(),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    const vetoId = await ctx.db.insert("vetos", {
      matchId: args.matchId,
      teamId: args.teamId,
      action: args.action,
      order: args.order,
      updateTime: args.updateTime,
    });

    return vetoId;
  },
});

export const nextStep = query({
  args: { matchId: v.id("matches") },
  async handler(ctx, args) {
    const match = await ctx.db.get(args.matchId);
    if (!match) throw new Error("Match not found");
    if (match.bestOf !== 3) return null;

    // Count existing vetos for this match
    let count = 0;
    const vetos = await ctx.db.query("vetos").withIndex("by_matchId", q => q.eq("matchId", args.matchId)).collect().catch(async () => {
      // Fallback without index
      const all = await ctx.db.query("vetos").collect();
      return all.filter(v => v.matchId === args.matchId);
    });
    count = vetos.length;
    const step = count + 1;

    // Fetch teams and determine who has first pick
    const team1 = await ctx.db.get(match.team1);
    const team2 = await ctx.db.get(match.team2);
    if (!team1 || !team2) throw new Error("Teams not found");
    const team1HasFirstPick = !!team1.hasFirstPick;

    let actingTeamId = match.team1;
    let action: "ban" | "pick" | "side_pick";
    switch (step) {
      case 1: actingTeamId = team1HasFirstPick ? match.team1 : match.team2; action = "ban"; break;
      case 2: actingTeamId = team1HasFirstPick ? match.team2 : match.team1; action = "ban"; break;
      case 3: actingTeamId = team1HasFirstPick ? match.team1 : match.team2; action = "pick"; break;
      case 4: actingTeamId = team1HasFirstPick ? match.team2 : match.team1; action = "side_pick"; break;
      case 5: actingTeamId = team1HasFirstPick ? match.team2 : match.team1; action = "pick"; break;
      case 6: actingTeamId = team1HasFirstPick ? match.team1 : match.team2; action = "side_pick"; break;
      case 7: actingTeamId = team1HasFirstPick ? match.team1 : match.team2; action = "ban"; break;
      case 8: actingTeamId = team1HasFirstPick ? match.team2 : match.team1; action = "ban"; break;
      default: return null; // veto complete
    }

    const actingTeam = actingTeamId.equals(match.team1) ? team1 : team2;
    return { captainId: actingTeam.captainId, action };
  },
});

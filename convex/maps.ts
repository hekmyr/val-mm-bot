import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const VALORANT_MAPS = [
  "ASCENT",
  "BIND",
  "HAVEN",
  "SPLIT",
  "FRACTURE",
  "LOTUS",
  "PEARL",
];

export const list = query({
  args: {},
  async handler(ctx) {
    return await ctx.db.query("maps").collect();
  },
});

export const getActive = query({
  args: {},
  async handler(ctx) {
    return await ctx.db
      .query("maps")
      .filter((q) => q.eq(q.field("isEnabled"), true))
      .collect();
  },
});

export const getByName = query({
  args: { name: v.string() },
  async handler(ctx, args) {
    const results = await ctx.db
      .query("maps")
      .filter((q) => q.eq(q.field("name"), args.name))
      .collect();
    return results.length > 0 ? results[0] : null;
  },
});

export const create = mutation({
  args: {
    name: v.string(),
    isEnabled: v.boolean(),
    updateTime: v.number(),
  },
  async handler(ctx, args) {
    const existing = await ctx.db
      .query("maps")
      .filter((q) => q.eq(q.field("name"), args.name))
      .collect();

    if (existing.length > 0) {
      throw new Error(`Map "${args.name}" already exists`);
    }

    const mapId = await ctx.db.insert("maps", {
      name: args.name,
      isEnabled: args.isEnabled,
      updateTime: args.updateTime,
    });

    return mapId;
  },
});

export const seedMaps = mutation({
  args: {},
  async handler(ctx) {
    const allMaps = await ctx.db.query("maps").collect();

    // Normalize existing maps to uppercase
    for (const map of allMaps) {
      if (map.name !== map.name.toUpperCase()) {
        await ctx.db.patch(map._id, {
          name: map.name.toUpperCase(),
          updateTime: Date.now(),
        });
      }
    }

    const activeMaps = allMaps
      .filter((m) => m.isEnabled)
      .map((m) => ({ ...m, name: m.name.toUpperCase() }));

    if (activeMaps.length > 7) {
      throw new Error(
        `Too many active maps: ${activeMaps.length} (expected 7)`,
      );
    }

    if (activeMaps.length === 7) {
      return {
        message: "Maps already seeded correctly",
        count: activeMaps.length,
      };
    }

    const existingNames = new Set(activeMaps.map((m) => m.name));
    const createdMaps = [];

    for (const mapName of VALORANT_MAPS) {
      if (!existingNames.has(mapName)) {
        const mapId = await ctx.db.insert("maps", {
          name: mapName,
          isEnabled: true,
          updateTime: Date.now(),
        });
        createdMaps.push({ name: mapName, id: mapId });
      }
    }

    return {
      message: "Maps seeded successfully",
      previousCount: activeMaps.length,
      added: createdMaps.length,
      maps: createdMaps,
    };
  },
});

const MAP_POOL_COUNT = 7;

export const validate = query({
  args: {},
  async handler(ctx) {
    const enableMaps = await ctx.db
      .query("maps")
      .filter((q) => q.eq(q.field("isEnabled"), true))
      .collect();

    return enableMaps.length === MAP_POOL_COUNT;
  },
});

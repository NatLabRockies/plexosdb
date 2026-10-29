import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { runInNewContext } from "node:vm";

const script = readFileSync(new URL("./public/legacy-redirect.js", import.meta.url), "utf8");
const members = JSON.parse(readFileSync(new URL("./public/api-fragments.json", import.meta.url), "utf8"));

function redirected(hash, canonical) {
  return new Promise((resolve) => {
    runInNewContext(script, {
      document: { querySelector: () => ({ getAttribute: () => canonical }) },
      window: { location: { pathname: "/plexosdb/api/plexosdb.html", hash, replace: resolve } },
      fetch: async () => ({ ok: true, json: async () => members }),
      console,
    });
  });
}

test("legacy API member bookmarks resolve to generated references", async () => {
  const member = "plexosdb.db.PlexosDB.add_object";
  assert.ok(members[member]);
  assert.equal(await redirected(`#${member}`, "/plexosdb/reference/api/modules/plexosdb/"), members[member]);
});

test("unmapped guide fragments remain attached to their redirected page", async () => {
  assert.equal(
    await redirected("#create-a-database", "/plexosdb/how-to/create_db/"),
    "/plexosdb/how-to/create_db/#create-a-database",
  );
});
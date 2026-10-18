import test from "node:test"
import assert from "node:assert/strict"
import { matchNames } from "./nameMatch.ts"

test("allows an initial and ignores honorifics", () =>
  assert.equal(matchNames("Sunita Devi", "Sunita D.").matched, true))
test("matches a known Devanagari spelling", () =>
  assert.equal(matchNames("सुनीता देवी", "Sunita Devi").matched, true))
test("rejects a clearly different name", () =>
  assert.equal(matchNames("Sunita Devi", "Meena Sharma").matched, false))

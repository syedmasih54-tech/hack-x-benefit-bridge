import test from "node:test"
import assert from "node:assert/strict"
import { evaluateRules, type Intake, type Rule } from "./rules.ts"

const intake: Intake = {
  state: "UP",
  district: "Lucknow",
  age: "62",
  gender: "female",
  maritalStatus: "widowed",
  rationCard: "bpl",
  bankAccount: "yes",
  name: "Sunita Devi",
}

test("rules engine reports matching and missing conditions deterministically", () => {
  const rules: Rule[] = [
    {
      id: "age",
      label_hi: "आयु",
      label_en: "Age",
      field: "age",
      operator: "min",
      value: 60,
      source_url: "#",
      version: "placeholder",
      last_verified: null,
      placeholder: true,
    },
    {
      id: "state",
      label_hi: "राज्य",
      label_en: "State",
      field: "state",
      operator: "equals",
      value: "BR",
      source_url: "#",
      version: "placeholder",
      last_verified: null,
      placeholder: true,
    },
  ]
  assert.deepEqual(
    evaluateRules(intake, rules).map(({ matched }) => matched),
    [true, false],
  )
})

export type Intake = {
  state: string
  district: string
  age: string
  gender: string
  maritalStatus: string
  rationCard: string
  bankAccount: string
  name: string
}

export type Rule = {
  id: string
  label_hi: string
  label_en: string
  field: keyof Intake
  operator: "equals" | "min"
  value: string | number
  source_url: string
  version: string
  last_verified: string | null
  placeholder: boolean
}

export type RuleResult = Rule & { matched: boolean }

export function evaluateRules(intake: Intake, rules: Rule[]): RuleResult[] {
  return rules.map((rule) => {
    const actual = intake[rule.field]
    const matched =
      rule.operator === "min"
        ? Number(actual) >= Number(rule.value)
        : actual === String(rule.value)
    return { ...rule, matched }
  })
}

const honorifics = new Set([
  "devi",
  "kumari",
  "smt",
  "srimati",
  "श्रीमती",
  "कुमारी",
  "देवी",
])

const devanagariWords: Record<string, string> = {
  सुनीता: "sunita",
  सुनिता: "sunita",
  देवी: "devi",
  कुमारी: "kumari",
  श्रीमती: "smt",
}

function romanize(value: string) {
  return value
    .split(/\s+/)
    .map((part) => devanagariWords[part] ?? part)
    .join(" ")
}

export function normalizeName(value: string) {
  return romanize(value)
    .toLocaleLowerCase("en")
    .replace(/[^\p{L}\s]/gu, " ")
    .split(/\s+/)
    .filter(Boolean)
    .filter((part) => !honorifics.has(part))
}

function levenshtein(a: string, b: string) {
  const matrix = Array.from({ length: b.length + 1 }, (_, i) => [i])
  for (let j = 0; j <= a.length; j += 1) matrix[0][j] = j
  for (let i = 1; i <= b.length; i += 1) {
    for (let j = 1; j <= a.length; j += 1) {
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + (a[j - 1] === b[i - 1] ? 0 : 1),
      )
    }
  }
  return matrix[b.length][a.length]
}

export function matchNames(first: string, second: string) {
  const a = normalizeName(first)
  const b = normalizeName(second)
  if (!a.length || !b.length) return { score: 0, matched: false }
  const initialCompatible = (left: string, right: string) =>
    left === right ||
    (left.length === 1 && right.startsWith(left)) ||
    (right.length === 1 && left.startsWith(right))
  const tokenMatches = a.filter((token) =>
    b.some((other) => initialCompatible(token, other)),
  ).length
  const tokenScore = tokenMatches / Math.max(a.length, b.length)
  const joinedA = a.join("")
  const joinedB = b.join("")
  const editScore =
    1 - levenshtein(joinedA, joinedB) / Math.max(joinedA.length, joinedB.length)
  const score = Math.max(tokenScore, editScore)
  return {
    score: Math.max(0, Math.round(score * 100) / 100),
    matched: score >= 0.72,
  }
}

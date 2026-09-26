import { describe, expect, it } from "vitest"

import { formatDuration, formatDureeMinutes } from "./duration"

describe("formatDuration", () => {
  it("formate en mm:ss sous une heure", () => {
    expect(formatDuration(0)).toBe("00:00")
    expect(formatDuration(5)).toBe("00:05")
    expect(formatDuration(65)).toBe("01:05")
    expect(formatDuration(3599)).toBe("59:59")
  })

  it("formate en h:mm:ss à partir d'une heure", () => {
    expect(formatDuration(3600)).toBe("1:00:00")
    expect(formatDuration(3661)).toBe("1:01:01")
    expect(formatDuration(7325)).toBe("2:02:05")
  })
})

describe("formatDureeMinutes", () => {
  it("dit la durée d'une épreuve en langage courant", () => {
    expect(formatDureeMinutes(45)).toBe("45 min")
    expect(formatDureeMinutes(120)).toBe("2 h")
    expect(formatDureeMinutes(90)).toBe("1 h 30")
    expect(formatDureeMinutes(185)).toBe("3 h 05")
  })
})

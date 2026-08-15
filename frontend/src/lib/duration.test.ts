import { describe, expect, it } from "vitest"

import { formatDuration } from "./duration"

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

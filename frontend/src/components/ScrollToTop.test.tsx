import { render } from "@testing-library/react"
import { Link, MemoryRouter, Route, Routes } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import userEvent from "@testing-library/user-event"

import { ScrollToTop } from "./ScrollToTop"

describe("ScrollToTop", () => {
  const scrollTo = vi.fn()

  beforeEach(() => {
    scrollTo.mockReset()
    window.scrollTo = scrollTo as unknown as typeof window.scrollTo
  })
  afterEach(() => vi.restoreAllMocks())

  function monter() {
    return render(
      <MemoryRouter initialEntries={["/liste"]}>
        <ScrollToTop />
        <Routes>
          <Route path="/liste" element={<Link to="/detail">ouvrir</Link>} />
          <Route path="/detail" element={<p>détail</p>} />
        </Routes>
      </MemoryRouter>,
    )
  }

  it("remonte en haut SANS animation quand on change de page", async () => {
    monter()
    scrollTo.mockClear() // le premier rendu compte aussi comme une arrivée
    await userEvent.click(document.querySelector("a")!)
    // index.css pose `scroll-behavior: smooth` sur <html> : sans « instant », la remontée s'anime et la page plus
    // courte l'interrompt au milieu (test élève 2026-11-07 : 2500 px avant le clic, 1452 px après).
    expect(scrollTo).toHaveBeenCalledWith({ top: 0, left: 0, behavior: "instant" })
  })
})

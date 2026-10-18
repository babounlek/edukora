import { act, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import * as ReactRouter from "react-router-dom"
import { Link, Route, Routes, unstable_HistoryRouter as HistoryRouter, useLocation, useParams } from "react-router-dom"
import { afterEach, describe, expect, it } from "vitest"

import { creerHistoriqueAnglais } from "./historiqueAnglais"

function Page() {
  const { slug } = useParams()
  const { pathname } = useLocation()
  return (
    <div>
      <p data-testid="interne">{pathname}</p>
      <p data-testid="slug">{slug}</p>
      <Link to="/cm/cours">cours</Link>
      <Link to="/cm/epreuves/maths-2023/lire?x=1#haut">lecteur</Link>
      <Link to="/tarifs">tarifs</Link>
    </div>
  )
}

function monter(urlPublique: string) {
  window.history.replaceState(null, "", urlPublique)
  const historique = creerHistoriqueAnglais()
  render(
    <HistoryRouter history={historique}>
      <Routes>
        <Route path="/:country/epreuves/:slug" element={<Page />} />
        <Route path="/:country/cours" element={<Page />} />
        <Route path="/tarifs" element={<Page />} />
      </Routes>
    </HistoryRouter>,
  )
}

afterEach(() => window.history.replaceState(null, "", "/"))

describe("historique du routeur anglais", () => {
  it("dépend bien de ces deux exports de react-router (à revoir si react-router change)", () => {
    expect(typeof ReactRouter.UNSAFE_createBrowserHistory).toBe("function")
    expect(typeof ReactRouter.unstable_HistoryRouter).toBe("function")
  })

  it("le routeur voit des chemins français : routes, useParams et useLocation sont inchangés", () => {
    monter("/en/cm/past-papers/maths-2023")
    expect(screen.getByTestId("interne").textContent).toBe("/cm/epreuves/maths-2023")
    expect(screen.getByTestId("slug").textContent).toBe("maths-2023")
  })

  it("les href des liens sont publics : anglais, sous /en, query et ancre conservées", () => {
    monter("/en/cm/past-papers/maths-2023")
    expect(screen.getByText("cours").getAttribute("href")).toBe("/en/cm/lessons")
    expect(screen.getByText("lecteur").getAttribute("href")).toBe("/en/cm/past-papers/maths-2023/read?x=1#haut")
    expect(screen.getByText("tarifs").getAttribute("href")).toBe("/en/pricing")
  })

  it("une navigation écrit l'adresse anglaise dans la barre d'adresse", async () => {
    monter("/en/cm/past-papers/maths-2023")
    await userEvent.click(screen.getByText("cours"))
    expect(window.location.pathname).toBe("/en/cm/lessons")
    expect(screen.getByTestId("interne").textContent).toBe("/cm/cours")
  })

  it("le retour arrière relit l'adresse anglaise comme un chemin interne", async () => {
    monter("/en/cm/past-papers/maths-2023")
    await userEvent.click(screen.getByText("tarifs"))
    expect(screen.getByTestId("interne").textContent).toBe("/tarifs")
    act(() => window.history.back())
    await screen.findByText("/cm/epreuves/maths-2023")
    expect(window.location.pathname).toBe("/en/cm/past-papers/maths-2023")
  })

  it("une URL anglaise aux segments français est réécrite sur place en sa forme anglaise", () => {
    monter("/en/cm/epreuves/maths-2023?x=1#haut")
    expect(window.location.pathname + window.location.search + window.location.hash).toBe(
      "/en/cm/past-papers/maths-2023?x=1#haut",
    )
    expect(screen.getByTestId("interne").textContent).toBe("/cm/epreuves/maths-2023")
  })
})

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { act, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const { listQuizEssais } = vi.hoisted(() => ({ listQuizEssais: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ listQuizEssais, startQuizEssai: vi.fn() }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))

import { definirLangue } from "@/lib/i18n"
import { EssaisGratuitsQuiz } from "./EssaisGratuitsQuiz"

const essai = (cursus: number, display: string, langue: "fr" | "en", subject: string, theme = "Theme") => ({
  cursus, cursus_display: display, langue,
  subject: cursus * 10, subject_label: subject, subject_code: "MATHS",
  theme: cursus * 100, theme_name: theme, nb_questions: 6,
})
const ESSAIS = [
  essai(3, "BAC - Série A", "fr", "Mathématiques"),
  essai(4, "BAC - Série C", "fr", "Physique"),
  essai(14, "BEPC", "fr", "Géographie"),
  essai(30, "GCE O Level", "en", "Mathematics"),
]

function afficher(cursusInitial?: number | null) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <EssaisGratuitsQuiz cursusInitial={cursusInitial} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => listQuizEssais.mockResolvedValue(ESSAIS))
afterEach(async () => {
  await definirLangue("fr", { persister: false })
  listQuizEssais.mockReset()
})

describe("EssaisGratuitsQuiz : examens de la langue de l'interface", () => {
  it("en français : BAC et BEPC, jamais le GCE, premier examen français par défaut", async () => {
    afficher()
    expect(await screen.findByRole("button", { name: "BEPC" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "BAC - A" })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "GCE O Level" })).not.toBeInTheDocument()
    expect(screen.getByText("Mathématiques")).toBeInTheDocument()
  })

  it("en anglais : le GCE seul, ses essais affichés d'emblée, sans examen français", async () => {
    await definirLangue("en", { persister: false })
    afficher()
    expect(await screen.findByText("Mathematics")).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "BEPC" })).not.toBeInTheDocument()
    expect(screen.queryByText("Mathématiques")).not.toBeInTheDocument()
  })

  it("l'examen déclaré dans l'autre langue n'est pas proposé", async () => {
    await definirLangue("en", { persister: false })
    afficher(14)
    expect(await screen.findByText("Mathematics")).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "BEPC" })).not.toBeInTheDocument()
    expect(screen.queryByText("Géographie")).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "BAC - A" })).not.toBeInTheDocument()
  })

  it("rien à offrir dans la langue : pas de section", async () => {
    listQuizEssais.mockResolvedValue(ESSAIS.filter((e) => e.langue === "fr"))
    await definirLangue("en", { persister: false })
    const { container } = afficher()
    await act(async () => {})
    expect(listQuizEssais).toHaveBeenCalled()
    expect(container.querySelector("section")).toBeNull()
  })
})

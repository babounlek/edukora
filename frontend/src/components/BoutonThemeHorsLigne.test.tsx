import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { PaquetTheme } from "@/lib/pwa"

const pwa = vi.hoisted(() => ({
  activerLeHorsLigne: vi.fn(), estThemeDisponibleHorsLigne: vi.fn(), nombreElementsDuPaquet: vi.fn(), telechargerTheme: vi.fn(),
  retirerTheme: vi.fn(), espaceUtilise: vi.fn(), tailleLisible: vi.fn((o: number) => `${o} o`),
  useEnLigne: vi.fn(() => true),
}))
const toast = vi.hoisted(() => ({ success: vi.fn(), error: vi.fn() }))
vi.mock("@/lib/pwa", () => pwa)
vi.mock("sonner", () => ({ toast }))

import { BoutonThemeHorsLigne } from "./BoutonThemeHorsLigne"

const paquet = { cursusId: 4, tagId: 9, subject: "MATHS", liste: {} } as unknown as PaquetTheme

describe("BoutonThemeHorsLigne", () => {
  beforeEach(() => {
    Object.values(pwa).forEach((f) => f.mockReset())
    pwa.useEnLigne.mockReturnValue(true)
    pwa.nombreElementsDuPaquet.mockReturnValue(5)
    pwa.estThemeDisponibleHorsLigne.mockResolvedValue(false)
    pwa.activerLeHorsLigne.mockResolvedValue(true)
    pwa.telechargerTheme.mockResolvedValue(0)
    pwa.retirerTheme.mockResolvedValue(undefined)
    pwa.espaceUtilise.mockResolvedValue({ usage: 2048, quota: 100000 })
    pwa.tailleLisible.mockImplementation((o: number) => `${o} o`)
    Object.defineProperty(window, "caches", { value: {}, configurable: true })
    Object.defineProperty(navigator, "serviceWorker", { value: {}, configurable: true })
  })

  it("propose le téléchargement avec le nombre d'éléments, active le hors-ligne puis télécharge", async () => {
    render(<BoutonThemeHorsLigne paquet={paquet} />)
    fireEvent.click(await screen.findByRole("button", { name: "Télécharger ce thème (5 éléments)" }))
    await waitFor(() => expect(pwa.telechargerTheme).toHaveBeenCalled())
    expect(pwa.activerLeHorsLigne).toHaveBeenCalled()
    await waitFor(() => expect(toast.success).toHaveBeenCalled())
    expect(await screen.findByText("Thème disponible hors connexion")).toBeTruthy()
  })

  it("dit quand le navigateur ne peut pas, sans rien télécharger", async () => {
    pwa.activerLeHorsLigne.mockResolvedValue(false)
    render(<BoutonThemeHorsLigne paquet={paquet} />)
    fireEvent.click(await screen.findByRole("button"))
    await waitFor(() => expect(toast.error).toHaveBeenCalled())
    expect(pwa.telechargerTheme).not.toHaveBeenCalled()
  })

  it("signale un paquet incomplet et garde le bouton", async () => {
    pwa.telechargerTheme.mockResolvedValue(2)
    render(<BoutonThemeHorsLigne paquet={paquet} />)
    fireEvent.click(await screen.findByRole("button"))
    await waitFor(() => expect(toast.error).toHaveBeenCalledWith(expect.stringContaining("2 éléments")))
    expect(screen.getByRole("button")).toBeTruthy()
  })

  it("se tait hors connexion et quand rien n'est à garder", async () => {
    pwa.nombreElementsDuPaquet.mockReturnValue(1)
    const { container } = render(<BoutonThemeHorsLigne paquet={paquet} />)
    await waitFor(() => expect(pwa.estThemeDisponibleHorsLigne).toHaveBeenCalled())
    expect(container.textContent).toBe("")
  })

  it("un thème gardé dit la place occupée et peut être retiré de l'appareil", async () => {
    pwa.estThemeDisponibleHorsLigne.mockResolvedValue(true)
    render(<BoutonThemeHorsLigne paquet={paquet} />)

    expect(await screen.findByText("Thème disponible hors connexion")).toBeTruthy()
    expect(await screen.findByText("EduKora occupe 2048 o sur cet appareil.")).toBeTruthy()

    fireEvent.click(screen.getByRole("button", { name: "Retirer de cet appareil" }))

    await waitFor(() => expect(pwa.retirerTheme).toHaveBeenCalledWith(paquet))
    expect(await screen.findByRole("button", { name: /Télécharger ce thème/ })).toBeTruthy() // il se retélécharge d'un geste
    expect(toast.success).toHaveBeenCalled()
  })

  it("sans estimation de place par le navigateur, la ligne d'espace n'apparaît pas", async () => {
    pwa.estThemeDisponibleHorsLigne.mockResolvedValue(true)
    pwa.espaceUtilise.mockResolvedValue(null)
    render(<BoutonThemeHorsLigne paquet={paquet} />)

    expect(await screen.findByText("Thème disponible hors connexion")).toBeTruthy()
    expect(screen.queryByText(/occupe/)).toBeNull()
  })
})

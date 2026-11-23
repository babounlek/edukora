import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it } from "vitest"

import { PHOTO_FONDATEUR } from "@/lib/site"

import { MotDuFondateur, dureeSansRepetiteur } from "./MotDuFondateur"

describe("dureeSansRepetiteur : la phrase reste vraie sans qu'on y retouche", () => {
  it("dit trois mois le jour où le mot a été écrit, puis avance d'un mois à la fois", () => {
    expect(dureeSansRepetiteur(new Date(2026, 10, 22))).toBe("trois mois")
    expect(dureeSansRepetiteur(new Date(2026, 11, 21))).toBe("trois mois")
    expect(dureeSansRepetiteur(new Date(2026, 11, 22))).toBe("quatre mois")
    expect(dureeSansRepetiteur(new Date(2027, 6, 30))).toBe("onze mois")
  })

  it("passe à l'année quand elle est faite", () => {
    expect(dureeSansRepetiteur(new Date(2027, 7, 22))).toBe("plus d'un an")
    expect(dureeSansRepetiteur(new Date(2028, 7, 21))).toBe("plus d'un an")
    expect(dureeSansRepetiteur(new Date(2028, 7, 22))).toBe("plus de 2 ans")
  })

  it("ne descend jamais sous trois mois, même avec une horloge d'appareil en retard", () => {
    expect(dureeSansRepetiteur(new Date(2026, 8, 1))).toBe("trois mois")
    expect(dureeSansRepetiteur(new Date(2020, 0, 1))).toBe("trois mois")
  })
})

describe("MotDuFondateur : une personne, son nom, et son lien avec le site", () => {
  it("dit pourquoi le site existe, sous un titre qui n'est pas celui d'un avis", () => {
    render(<MotDuFondateur />)

    expect(screen.getByText("Pourquoi j'ai créé EduKora")).toBeInTheDocument()
    expect(screen.getByText(/pour mon fils, qui prépare le BEPC/)).toBeInTheDocument()
    expect(screen.getByText(/au lieu de payer un répétiteur/)).toBeInTheDocument()
  })

  it("signe du nom et des deux qualités : parent ET fondateur, jamais un parent anonyme", () => {
    render(<MotDuFondateur />)

    expect(screen.getByText("Serge G. Babounlek")).toBeInTheDocument()
    expect(screen.getByText(/parent d'un élève de 3e et fondateur d'EduKora/)).toBeInTheDocument()
  })

  it("ne promet rien pour l'enfant d'un autre : c'est une expérience, pas une garantie", () => {
    render(<MotDuFondateur />)

    const citation = screen.getByText(/pour mon fils/).textContent ?? ""
    expect(citation).not.toMatch(/votre enfant|ton enfant|garanti|réussi/i)
  })
})

describe("MotDuFondateur, variante bande : le mot en grand sur l'accueil", () => {
  function rendre() {
    return render(
      <MemoryRouter>
        <MotDuFondateur variante="bande" />
      </MemoryRouter>,
    )
  }

  it("garde le titre, la citation et la signature, et mène à la page « À propos »", () => {
    rendre()

    expect(screen.getByText("Pourquoi j'ai créé EduKora")).toBeInTheDocument()
    expect(screen.getByText(/pour mon fils, qui prépare le BEPC/)).toBeInTheDocument()
    expect(screen.getByText("Serge G. Babounlek")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Qui est derrière EduKora/ })).toHaveAttribute("href", "/a-propos")
  })

  it("montre la photo du fondateur quand il y en a une, et jamais un cadre vide", () => {
    const { container } = rendre()

    const images = container.querySelectorAll("img")
    if (PHOTO_FONDATEUR) {
      expect(images).toHaveLength(1)
      expect(images[0]).toHaveAttribute("src", PHOTO_FONDATEUR.src)
      expect(images[0]).toHaveAccessibleName(/Serge G. Babounlek/)
    } else {
      expect(images).toHaveLength(0)
    }
  })
})

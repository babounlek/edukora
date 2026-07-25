import { useEffect } from "react"

import { SITE_NAME } from "@/lib/site"

// Générique, sans nom de pays : cette valeur par défaut sert des pages qui ne sont pas
// spécifiques à un pays (compte, connexion, lecture...) - un pays en dur induirait en
// erreur un visiteur d'un autre pays (voir CataloguePage/CoursListPage pour la
// description propre à chaque pays affichée sur les pages qui, elles, en dépendent).
const DEFAULT_DESCRIPTION =
  "Corrigés d'annales, sujets et cours pour le BEPC, le Probatoire et le BAC, rédigés par des enseignants."

function upsertMeta(attr: "name" | "property", key: string, content: string) {
  let tag = document.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`)
  if (!tag) {
    tag = document.createElement("meta")
    tag.setAttribute(attr, key)
    document.head.appendChild(tag)
  }
  tag.setAttribute("content", content)
}

interface SeoOptions {
  title: string
  description?: string
}

/**
 * SPA sans rendu serveur : Googlebot exécute le JS et voit ces balises, mais les
 * bots qui ne l'exécutent pas (aperçus de lien WhatsApp/Facebook) ne verront que
 * les balises statiques par défaut d'index.html, pas ce hook - limite acceptée
 * plutôt qu'une migration SSR pour ce besoin.
 */
export function useSeo({ title, description = DEFAULT_DESCRIPTION }: SeoOptions) {
  useEffect(() => {
    const fullTitle = `${title} | ${SITE_NAME}`
    document.title = fullTitle
    upsertMeta("name", "description", description)
    upsertMeta("property", "og:title", fullTitle)
    upsertMeta("property", "og:description", description)
  }, [title, description])
}

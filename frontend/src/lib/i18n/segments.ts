/**
 * Les segments d'URL en anglais : `/en/cm/past-papers/x/read` au lieu de `/en/cm/epreuves/x/lire`.
 *
 * Le routeur, lui, ne voit JAMAIS l'anglais : toutes ses routes, tous les `<Link to="...">`, `useParams`
 * et les comparaisons de chemin (`pathname.startsWith("/epreuves")`) restent en français « interne ».
 * Seule l'adresse réelle du navigateur (et les `href` des liens) est traduite, à la frontière : voir
 * historiqueAnglais.ts. Ce module ne contient donc que la traduction d'un chemin, dans les deux sens.
 *
 * Un chemin n'est traduit que s'il correspond à une route connue (`patrons`) : seuls les segments
 * FIXES de la route sont traduits, jamais un segment dynamique. Un slug d'épreuve qui s'appellerait
 * « cours » reste donc « cours ».
 *
 * La table vient de segments-url.json, partagée avec le backend (sitemap, aperçus de liens, PDF).
 */
import donnees from "./segments-url.json"

export const SEGMENTS_EN: Readonly<Record<string, string>> = donnees.segments
export const PATRONS_INTERNES: readonly string[] = donnees.patrons

const SEGMENTS_FR: Readonly<Record<string, string>> = Object.fromEntries(
  Object.entries(SEGMENTS_EN).map(([fr, en]) => [en, fr]),
)

type Patron = { segments: string[] }

function decouper(chemin: string): string[] {
  return chemin.split("/").filter((s) => s !== "")
}

const estDynamique = (segment: string) => segment.startsWith(":")

/** Le patron et ses segments dans une langue (« :slug » reste « :slug »). */
function patronDans(patron: string, vers: "fr" | "en"): Patron {
  return {
    segments: decouper(patron).map((s) => (estDynamique(s) || vers === "fr" ? s : (SEGMENTS_EN[s] ?? s))),
  }
}

const PATRONS_FR: readonly Patron[] = PATRONS_INTERNES.map((p) => patronDans(p, "fr"))
const PATRONS_EN: readonly Patron[] = PATRONS_INTERNES.map((p) => patronDans(p, "en"))

function correspond(patron: Patron, segments: string[]): boolean {
  return (
    patron.segments.length === segments.length &&
    patron.segments.every((s, i) => estDynamique(s) || s === segments[i])
  )
}

/** Conserve l'éventuel slash final et la forme d'un chemin vide. */
function recomposer(segments: string[], original: string): string {
  const chemin = `/${segments.join("/")}`
  return original.length > 1 && original.endsWith("/") && chemin !== "/" ? `${chemin}/` : chemin
}

/**
 * Chemin interne (français) -> chemin public anglais. Un chemin inconnu (404, route future) est rendu
 * tel quel. `chemin` est un pathname seul : la query et l'ancre se traitent avant (voir traduireCible).
 */
export function cheminAnglais(interne: string): string {
  const segments = decouper(interne)
  const index = PATRONS_FR.findIndex((p) => correspond(p, segments))
  if (index === -1) return interne
  const modele = PATRONS_FR[index].segments
  return recomposer(
    segments.map((s, i) => (estDynamique(modele[i]) ? s : (SEGMENTS_EN[s] ?? s))),
    interne,
  )
}

/**
 * Chemin public anglais -> chemin interne (français). Un chemin qui n'est pas la forme anglaise d'une route
 * (par exemple une ancienne forme française sous `/en`) est rendu tel quel : le routeur l'affiche alors
 * quand même, et l'URL est corrigée ensuite (voir historiqueAnglais.ts).
 */
export function cheminInterne(anglais: string): string {
  const segments = decouper(anglais)
  const index = PATRONS_EN.findIndex((p) => correspond(p, segments))
  if (index === -1) return anglais
  const modele = PATRONS_EN[index].segments
  return recomposer(
    segments.map((s, i) => (estDynamique(modele[i]) ? s : (SEGMENTS_FR[s] ?? s))),
    anglais,
  )
}

/** Sépare `/chemin?query#ancre` en pathname et reste, pour ne traduire que le pathname. */
export function separerCible(cible: string): { pathname: string; reste: string } {
  const i = cible.search(/[?#]/)
  return i === -1 ? { pathname: cible, reste: "" } : { pathname: cible.slice(0, i), reste: cible.slice(i) }
}

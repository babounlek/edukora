import { useEffect, useState } from "react"

/**
 * Retourne `value`, mais avec un délai après chaque changement - pour dériver une clé
 * de query TanStack Query qui ne se met à jour qu'une fois l'utilisateur "installé"
 * sur une valeur (ex. la recherche texte du catalogue), sans déclencher une requête à
 * chaque frappe. Ne change jamais `value` lui-même : l'appelant reste libre de
 * l'utiliser tel quel ailleurs (ex. affiché immédiatement dans le champ de recherche,
 * écrit immédiatement dans l'URL) pendant que seule la version debouncée pilote le fetch.
 */
export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timeout = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(timeout)
  }, [value, delayMs])

  return debounced
}

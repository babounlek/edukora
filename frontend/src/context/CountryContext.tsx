import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { useLocation } from "react-router-dom"

import { listCountries } from "@/api/endpoints"
import type { Country } from "@/api/types"
import { COUNTRY_STORAGE_KEY, DEFAULT_COUNTRY_CODE, extractCountryFromPath } from "@/lib/countryPath"

interface CountryContextValue {
  /** Code pays courant (minuscule) : celui de l'URL si on est sur une route
   * préfixée, sinon le dernier choisi (localStorage), sinon DEFAULT_COUNTRY_CODE. */
  country: string
  countries: Country[]
  setCountry: (code: string) => void
}

const CountryContext = createContext<CountryContextValue | undefined>(undefined)

export function CountryProvider({ children }: { children: ReactNode }) {
  const location = useLocation()
  const urlCountry = extractCountryFromPath(location.pathname)

  const [stored, setStored] = useState(
    () => localStorage.getItem(COUNTRY_STORAGE_KEY) || DEFAULT_COUNTRY_CODE,
  )
  const [countries, setCountries] = useState<Country[]>([])

  useEffect(() => {
    listCountries().then(setCountries).catch(() => {})
  }, [])

  useEffect(() => {
    if (urlCountry && urlCountry !== stored) {
      localStorage.setItem(COUNTRY_STORAGE_KEY, urlCountry)
      setStored(urlCountry)
    }
  }, [urlCountry, stored])

  function setCountry(code: string) {
    localStorage.setItem(COUNTRY_STORAGE_KEY, code)
    setStored(code)
  }

  return (
    <CountryContext.Provider value={{ country: urlCountry ?? stored, countries, setCountry }}>
      {children}
    </CountryContext.Provider>
  )
}

export function useCountry() {
  const ctx = useContext(CountryContext)
  if (!ctx) throw new Error("useCountry must be used within CountryProvider")
  return ctx
}

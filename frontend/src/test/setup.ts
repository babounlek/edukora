import "@testing-library/jest-dom/vitest"

// jsdom n'implémente ni l'API Pointer Capture ni scrollIntoView, dont les primitives
// Radix (Select, Dialog) se servent dès le premier clic : sans ces bouchons, tout
// test qui ouvre un menu déroulant échoue sur "target.hasPointerCapture is not a
// function" plutôt que sur ce qu'il teste vraiment. Bouchons neutres : ils ne
// simulent aucun comportement, ils rendent seulement ces appels inoffensifs.
// Garde `typeof Element` : certaines suites tournent en environnement node, sans
// aucun DOM (voir l'en-tête @vitest-environment de src/lib/audit-rendu.test.ts).
if (typeof Element !== "undefined") {
  if (!Element.prototype.hasPointerCapture) {
    Element.prototype.hasPointerCapture = () => false
    Element.prototype.setPointerCapture = () => {}
    Element.prototype.releasePointerCapture = () => {}
  }
  if (!Element.prototype.scrollIntoView) {
    Element.prototype.scrollIntoView = () => {}
  }
}

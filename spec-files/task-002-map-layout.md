# Task 002 — Create Map Layout and Search Functionality

## Goal

Build the initial, usable Map page for the frontend using Leaflet and OpenStreetMap map tiles. Add a restaurant-name search interface backed by Nominatim that shows relevant location results below the search field.

**Definition of done:** A user can open the main page, see an interactive map centered on Boston, Massachusetts, submit a restaurant-name search, and read the returned results without interacting with the map or selecting a result. This is a UI and search foundation task, not a restaurant-discovery or data-persistence feature.

## Context and Dependencies

- Read `project-thesis.md` and `AGENTS.md` before starting; follow their established stack, conventions, and instructions. If there is a conflict, report it rather than silently changing architecture.
- Prior tasks or decisions: Task-001 (project setup).
- Dependencies/blockers: The frontend and backend from Task-001 can start locally.
- Reuse the existing application structure, routing, styles, HTTP utilities, and test tooling where practical. Do not introduce an additional framework or standalone service just for this task.

## In Scope

- Render Leaflet on the application's main Map page, with a default center of approximately **42.3601, -71.0589** (Boston, MA) and a zoom level appropriate for a city view.
- Make the map occupy the available page viewport/content area, with functional pan and zoom controls and correctly loaded map tiles.
- Display a restaurant-search input in the upper-left corner as an overlay above the map; the search field and its results should not push or resize the map.
- Allow the user to type a restaurant name and explicitly submit the search using **Enter** or a visible search control.
- Query Nominatim for place/restaurant matches and display up to **five** returned results in a readable dropdown/panel directly below the search field.
- Show each result's name and available location context (such as street, city, and state), using only information actually provided by the API. A single readable display label is acceptable when more structured fields are unavailable.
- Handle the basic search lifecycle: idle, loading, results found, no matches, and request failure.
- Keep the layout usable at desktop and mobile viewport widths, including scrollable results when needed.

## Out of Scope

- Selecting, clicking, navigating to, or taking any action on a search result.
- Re-centering, zooming, highlighting, or otherwise updating the map based on search results.
- Restaurant markers/pins, popups, clusters, shapes, or other custom map overlays.
- Database reads/writes, saved restaurants, favorites, lists, or restaurant-specific backend data models.
- User geolocation requests, location permissions, or automatic map centering on the user's position.
- Restaurant detail pages, reviews, ratings, filters, categories, or advanced discovery features.
- Live autocomplete / API requests on each keystroke.
- UI redesigns beyond what is needed for this Map page and its search control.

## Required Behavior / User Scenarios

1. **Initial load:** Opening the main page renders a usable Leaflet map centered on Boston. OpenStreetMap attribution is visible; no restaurant pins are present. The search field appears over the map near the upper-left corner.
2. **Text entry:** The user can type a restaurant name (for example, `110 Grill`) without triggering a network request on each keystroke. The map remains usable.
3. **Search submission:** Pressing Enter or activating the search button initiates one search operation and displays a loading indicator/message beneath the input until it completes.
4. **Search results:** If Nominatim returns matches, show up to five readable, distinct rows below the input, retaining useful location detail to distinguish similarly named places. Display the results returned by the service; **do not fabricate expected restaurant branches or hard-code example results**. Results are informational only and are not selectable in this task.
5. **No results:** If the service returns an empty result set, show a friendly `No matching locations found` message rather than an empty or broken panel.
6. **Failure:** If the request fails or is rate-limited, show a concise error message while keeping the search field and map usable.
7. **Input changes:** Submitting a new query replaces the previous results. Clear or hide stale results when the input is cleared; ignore any delayed response from an outdated request. Blank/whitespace-only queries must not call the API.
8. **Responsive layout:** At narrow viewport widths, the search interface remains accessible and does not cover the entire map; results stay within the viewport and can scroll if necessary.

## Implementation Constraints

- Follow the stack and principles in `project-thesis.md` and the repository instructions in `AGENTS.md`.
- Use **Leaflet** for map interaction and **OpenStreetMap** tiles with visible, correct attribution. Reuse existing map or styling dependencies if Task-001 already established them.
- Use **Nominatim's search endpoint** for this initial implementation, with a JSON response and a limited result count. Prefer Boston-area results using an appropriate geographic bias where supported; do not enforce a hard geographic boundary that unnecessarily prevents matches elsewhere. Nominatim is a geocoder, not a guaranteed complete restaurant directory.
- If using the public `nominatim.openstreetmap.org` service, comply with its published usage policy: **no client-side autocomplete**, **no more than one request per second for the entire application**, proper application identification through the HTTP request, visible attribution, and caching where appropriate. Prefer routing requests through the existing backend when needed for compliant identification, caching, and application-wide rate limiting; do not create a new server or database for this feature. Do not treat a per-browser throttle as an application-wide rate limit.
- Keep the Nominatim endpoint configurable so it can be replaced later if the app needs true autocomplete, broader POI coverage, or higher traffic. Avoid exposing secrets (none should be required for the public endpoint).
- Do not perform an API search automatically when the Map page first loads.
- Keep layout, search request logic, and presentation reasonably separated for maintainability; follow existing project patterns rather than introducing unnecessary abstractions.
- Accessible controls: provide an accessible input label, keyboard submission, visible focus treatment, and status/error text announced appropriately. Do not imply results are clickable if they are not.
- The agent may choose routine internal implementation details; do not make material architectural or product changes without approval.

## Acceptance Criteria

- [ ] The frontend main page loads without runtime errors and displays Leaflet map tiles centered on Boston, MA.
- [ ] The map fills the intended page area; dragging and built-in zoom controls work, and required OpenStreetMap attribution remains visible.
- [ ] A clearly visible search input is overlaid in the upper-left of the map without changing map dimensions.
- [ ] A non-empty restaurant-name query can be submitted by Enter or the search control; the UI renders the real API results (up to five) beneath the input.
- [ ] Returned entries include enough available place/location text to differentiate matches; no results are hard-coded.
- [ ] The UI gives meaningful loading, empty-results, and API-failure feedback.
- [ ] Empty submissions do not make requests; clearing the input removes stale results; older responses cannot replace results from a newer search.
- [ ] Search uses explicit submission rather than keystroke autocomplete and respects the applicable Nominatim usage restrictions.
- [ ] Layout and controls remain usable at a narrow/mobile viewport width.
- [ ] Relevant automated tests are included or updated for search submission, result rendering, empty/error states, and stale response handling, using mocked HTTP responses rather than relying on live public API responses.
- [ ] Any new configuration, attribution, or local setup needed is documented.
- [ ] No result-selection behavior, restaurant markers, database integration, geolocation permission, or other out-of-scope functionality was introduced.

## Verification

Use the project's existing package scripts and test commands from `package.json`, build configuration, and `AGENTS.md`; **do not assume command names before inspecting the repository**.

1. **Build / static checks:** Run the existing frontend build, lint, and type-check commands where available. Record the exact commands and results; the build must complete without errors.
2. **Automated tests:** Run the relevant frontend test suite. Mock Nominatim responses to verify: a query only sends on submit; up to five results render with labels; blank queries do not send; no results and failed requests show messages; a stale response does not overwrite newer results.
3. **Manual initial-load check:** Start the project using the documented local instructions, open the main page, and verify the Boston-centered map, map tiles, pan/zoom, attribution, and top-left search overlay. Confirm there are no custom restaurant markers.
4. **Manual successful-search check:** Submit `110 Grill` or another restaurant name with known OpenStreetMap coverage. Confirm a loading state followed by API-derived matches when available; the exact locations returned may vary with OSM data. Confirm searching does not alter the map.
5. **Manual edge-case check:** Submit a blank query, try a clearly unlikely name, and simulate a failed/rate-limited request. Verify the respective blank, empty, and failure behavior. Repeat a search after a failure to confirm recovery.
6. **Responsive / regression check:** Test the map and search panel at desktop and narrow/mobile viewport sizes. Confirm the overlay remains visible and the pre-existing application startup/navigation still works.
7. **Usage-policy check:** Inspect the request flow to confirm it is initiated only on explicit submit and that the chosen implementation respects the public service's application-wide rate limit and identification/attribution requirements.

If any check cannot be run, report it as **not verified** and explain why. Never claim a check passed without executing it.

## Open Questions / Approval Required

- **Assumed for this task:** Search is submit-to-search, not live autocomplete. The public Nominatim service prohibits client-side autocomplete, and replacing it with another provider is outside this task.
- **Implementation review:** If the current backend cannot reasonably enforce the public Nominatim service's requirements, flag the blocker and propose the smallest compliant option before adding a new provider, service, or infrastructure component.
- **No other product decisions expected.** Follow existing conventions for precise spacing, theme, zoom level, and route name.

## Completion Report

### Summary

Implemented a full-viewport Leaflet/React Leaflet map centered on Boston at zoom 13,
with a top-left restaurant search overlay and read-only results. Explicit submissions
use the existing FastAPI backend and return up to five real Nominatim place labels.
Loading, empty, failure, input clearing, and outdated response handling are included.
Implementation and automated verification are complete; visual/manual browser checks
remain unverified because the browser access host is unavailable.

### Files Changed

- `frontend/src/App.tsx`: main Map page composition.
- `frontend/src/MapView.tsx`: Boston map, OSM tiles, attribution, bottom-right zoom.
- `frontend/src/SearchPanel.tsx`: accessible submit form, statuses, informational results.
- `frontend/src/placeSearch.ts`: abortable HTTP request utility.
- `frontend/src/index.css`: viewport map and responsive, scrollable overlay styling.
- `frontend/src/App.test.tsx`: mocked search lifecycle and stale-response tests.
- `frontend/src/MapView.test.tsx`: real Leaflet mount, zoom controls, attribution, no markers.
- `frontend/vite.config.ts`: local `/api` proxy to FastAPI.
- `frontend/package.json`, `frontend/package-lock.json`: pinned Leaflet 1.9.4,
  React Leaflet 5.0.0, and Leaflet types 1.9.21.
- `backend/app/search.py`: isolated provider integration, normalization, in-memory
  caching, shared asynchronous limiter, timeout, and HTTP 429 backoff.
- `backend/app/main.py`: validated search endpoint, generic provider failure handling,
  and HTTP client cleanup.
- `backend/app/config.py`, `backend/.env.example`: configurable provider URL and identification.
- `backend/tests/test_search.py`: mocked provider contract, cache, concurrent throttling,
  blank/long input, malformed responses, empty results, and provider errors.
- `README.md`: setup, configuration, attribution, policy, and single-process limits.
- `spec-files/task-002-map-layout.md`: this completion report.

### Verification Results

Commands were executed from the corresponding frontend/backend directory.

| Check | Result | Evidence |
| --- | --- | --- |
| `npm run lint` | pass | ESLint exited 0 with zero warnings. |
| `npm test` | pass | 2 test files, 5 tests passed. |
| `npm run build` | pass | TypeScript checking and Vite production build succeeded, 61 modules transformed. |
| `.venv/bin/pytest` | pass | 9 tests passed; one existing Starlette/httpx deprecation warning. |
| `.venv/bin/ruff check .` | pass | All checks passed. |
| `.venv/bin/ruff format --check .` | pass | 8 files already formatted. |
| `git diff --check` | pass | No whitespace errors. |
| Local startup | pass | FastAPI started on port 8000; Vite started on port 5173. |
| `curl --fail --silent http://127.0.0.1:8000/health` | pass | Returned `{"status":"ok"}`. |
| `curl --fail --silent http://localhost:5173/` | pass | Served the Food Maps HTML entry. |
| `curl --silent --show-error 'http://localhost:5173/api/places/search?q=110%20Grill'` | pass | Real provider response through Vite/FastAPI: two 110 Grill matches, District Avenue in Boston and Forbes Road in Braintree. |
| Explicit submit, five-result cap, blank queries, loading, empty, failure, recovery, stale response protection | pass | Mocked frontend tests; no live API dependency in tests. |
| Leaflet component mount and required controls | pass | Real Leaflet jsdom test found map container, OSM attribution, zoom buttons, and no restaurant marker icons. |
| Usage-policy implementation review | pass for documented local topology | Every browser uses the one backend limiter; misses serialized at least 1.1 seconds apart, identified User-Agent, 24-hour bounded cache, configurable endpoint, visible attribution. No initial-load search or autocomplete. |
| Visual initial map, tile loading, pan/zoom interaction, attribution visibility | not verified | Browser tool returned `The browser access host is unavailable`; jsdom is not a visual or tile-network check. |
| Successful search / blank / empty / failure through browser UI | not verified | Browser unavailable; HTTP success and mocked component behavior verified separately. |
| Desktop/mobile layout and result scrolling | not verified | Responsive CSS implemented, but no browser host available for visual/interaction checks. |

### Decisions and Deviations

- Kept the established React/Vite/TypeScript, Tailwind, React Leaflet, and FastAPI stack.
  No new service, database tables, or restaurant persistence was added.
- The backend's existing httpx dependency handles provider requests. The frontend
  uses a same-origin relative API URL; Vite proxies it during local development.
- Boston `viewbox` with `bounded=0` biases rather than restricts searches.
- One backend process/worker serves the local single-user demo. Its lock and cache
  coordinate all browser sessions. Multiple workers/replicas are unsupported with the
  public provider until a shared limiter/cache or different provider is introduced.
- Cache: up to 256 case-insensitive queries, including empty matches, for 24 hours;
  resets on restart. Provider errors are not cached or automatically retried. HTTP
  429 delays further upstream requests for at least 60 seconds.
- No result selection, map movement on search, custom markers, geolocation, or
  other future product behavior was introduced.
- npm installation reported 10 moderate dependency advisories; dependency security
  upgrades were not included in this map/search task.

### Follow-Up

- Complete the unverified browser checks when browser access is available.
- Reassess provider policy and coordinate throttling/cache before public or multi-process deployment.
- PR/commit: none created.

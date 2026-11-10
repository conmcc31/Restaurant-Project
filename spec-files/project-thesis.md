# Food Maps — V1 Project Thesis

## Thesis

Food Maps is a map-first web application for recording restaurants a person has visited, when they visited, and short notes about the experience.

Food Maps is **not** intended to be another Yelp-style public review or rating platform. It is a personal food/travel diary that may eventually become a lightweight social experience: friends and family could share their visited places and discover ideas when traveling.

**V1 is a local, single-user portfolio demo.** Social sharing, accounts, and production deployment are future possibilities, not part of the initial release.

## Why We're Building This

The application should make it enjoyable to build a visual history of dining experiences: where someone has eaten, what they liked, and what they would recommend to a friend. Notes should feel like personal tips (for example, “Plenty of parking,” “Strong drinks,” or “Get the carrot cake”), not formal public reviews.

This is also a software-engineering portfolio project. Its development process should demonstrate spec-driven, agent-assisted implementation with documented design decisions, review, and verification—not merely generated code.

## V1 User Journey

1. A user opens a full-screen map. If location permission is available, the map starts near the user; otherwise it uses a documented fallback location.
2. The user searches for a restaurant by name and explicitly submits the search.
3. Search results show enough location information to distinguish similar restaurants.
4. The user selects a result and saves it to their map. Notes and recommendation status are optional.
5. The user can record the visit date, add brief notes, and choose **Recommend**, **Don't Recommend**, or neither.
6. Saved restaurants appear as map pins. Selecting a pin displays a popup with the restaurant name, location, and the date it was added, plus a way to open its details.
7. A details sidebar shows the saved restaurant, visit information, recommendation, and notes. The user can edit the saved information or remove the restaurant from their map.
8. Saved data remains available across browser refreshes and application restarts.

## V1 Scope and Success Criteria

V1 is complete when all of the following are demonstrably working:

- [ ] Restaurant search returns selectable, identifiable locations.
- [ ] A selected restaurant can be saved to the user's map without requiring notes or a recommendation.
- [ ] A saved restaurant has a visit date and can optionally store notes and a recommendation.
- [ ] Saved restaurants appear as pins and open their details.
- [ ] A saved entry can be edited and removed.
- [ ] Data persists in PostgreSQL across application restarts.
- [ ] The application starts in a documented, reproducible local development environment.
- [ ] Core behavior is validated with appropriate automated and/or manual tests.

### Explicitly Outside V1

- User registration, login, authentication, and authorization
- Friend connections, shared maps, or multi-user collaboration
- Public reviews, star ratings, moderation, or monetization
- Native mobile applications
- Production hosting, scaling, analytics, or advanced observability
- Complex visit-history features beyond the initial agreed V1 data model

## Technology Decisions

| Area | V1 choice | Rationale |
| --- | --- | --- |
| Repository | Monorepo with `frontend/` and `backend/` | Easy to review and run as one portfolio project |
| Frontend | React + Vite + TypeScript | Component-based UI with compile-time type checking |
| Styling | Tailwind CSS | Lightweight, consistent UI styling |
| Map UI | Leaflet + React Leaflet | Interactive map and pins |
| Backend | Python + FastAPI | Typed request/response models and straightforward API development |
| Backend validation | Pydantic (via FastAPI) | Explicit API data contracts |
| Database | PostgreSQL | Relational persistence |
| Database access | SQLAlchemy + PostgreSQL driver | Isolated persistence layer |
| Schema migrations | Alembic | Versioned changes when tables are introduced |
| Local services | Docker Compose for PostgreSQL | Reproducible local database |
| Backend tests/quality | pytest + Ruff | Tests and static checks |
| Frontend tests/quality | Vitest + React Testing Library + ESLint | Component tests and lint checks as UI is added |
| Place search | Nominatim / OpenStreetMap, subject to provider policy | Initial educational prototype, replaceable integration |

Use supported, mutually compatible stable versions when each dependency is introduced. Record actual selected versions in dependency manifests and lockfiles where supported. New dependencies must have a clear purpose.

## Architectural Principles

- The React frontend communicates with the backend through APIs; it never connects directly to PostgreSQL.
- The backend owns data validation and persistence. SQLAlchemy is used for database access.
- Keep external place-search integration behind a replaceable interface or module; do not tie core saved-restaurant behavior to one provider's response format.
- Favor small, understandable modules over speculative abstractions, microservices, or unnecessary infrastructure.
- Use environment variables for configuration; never commit secrets. Provide example configuration files.
- Preserve room for future social/multi-user features without implementing those features in V1.
- Handle unavailable geolocation, failed searches, empty results, and missing optional notes gracefully.
- Each implementation task must define observable acceptance criteria and report which checks were actually run.

## Map and Place-Search Provider Constraints

- The public Nominatim service is only a potential provider for **explicitly submitted** searches, not live search-as-you-type or autocomplete.
- If using `nominatim.openstreetmap.org`, comply with its published policy, including a maximum of **one request per second across the application**, identifying requests, attribution, appropriate caching, and the ability to switch providers. Do not implement prohibited autocomplete or systematic place scraping.
- If the intended UX eventually needs autocomplete or higher traffic, select an appropriate provider or deployment arrangement before implementing it.
- If using OpenStreetMap Foundation map tiles, follow the tile usage policy, including visible attribution and appropriate caching/request behavior. Avoid bulk tile downloading.
- **Educational or noncommercial intent does not remove provider-policy obligations.** Reassess providers, licensing, privacy, and hosting before a public launch.

Policy references:
- https://operations.osmfoundation.org/policies/nominatim/
- https://operations.osmfoundation.org/policies/tiles/

## Design Expectations

### Base Map Layout

- The map fills the main browser viewport.
- A search control overlays the upper-left portion of the map.
- Search is triggered by an explicit submit action; a result list allows the user to choose a location.
- Selecting a restaurant can reveal a details sidebar where the user may add visit information or save the location with optional fields blank.
- Geolocation permission is optional; a sensible default view is shown if unavailable.

### Map Pins

- Saved restaurants are displayed as pins.
- Selecting a pin opens a compact popup with its name, location, the date added to the map, and an action to view details.
- Map interactions must not depend on the user supplying notes or a recommendation.

### Details Sidebar

- A sidebar opens on the right side of the map when viewing or editing a restaurant.
- It displays the restaurant's identifying details, visit date, optional recommendation status, and optional notes.
- A user can edit these fields or remove the entry from their map.
- Responsive behavior for smaller screens should be planned during the relevant UI task.

## Open Decisions — Resolve Before Relevant Implementation

These are **not** instructions for the agent to decide silently. Record the chosen approach in the relevant task or an architecture decision before implementing the affected feature.

1. **Visit history:** Is V1 one saved record per restaurant, or can users log multiple visits to the same restaurant? The original product idea supports visit dates, but does not settle repeated visits.
2. **Duplicate locations:** What should happen if a user saves the same restaurant again?
3. **Single-user identity:** Should V1 store records without a user entity, or use a fixed demo user to simplify later multi-user support?
4. **Restaurant identity:** How should provider place IDs and coordinates be normalized, and what happens if a result lacks a stable provider ID?
5. **Date semantics:** Is a visit date required, and should it default to today's date? Keep the date visited distinct from the timestamp when the entry was added.
6. **Default map view:** What fallback city/region should be shown when geolocation is denied?
7. **Search provider fit:** Validate that the chosen provider provides sufficient restaurant results in intended demo regions before committing to it.

## Development and Documentation Workflow

- `project-thesis.md` defines the product intent and durable constraints.
- `AGENTS.md` contains standing agent operating rules.
- `tasks/*.md` defines one bounded implementation task at a time.
- A task is complete only after its acceptance criteria have been checked, with failures and unverified items explicitly reported.
- Material architectural decisions and deviations should be recorded in task completion notes or a brief decision record; link significant tasks to their PR or commit when available.
- Agents should surface conflicts between the task and thesis rather than silently overriding either.

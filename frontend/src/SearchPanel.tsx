import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { canSave, savePlace, searchPlaces } from './placeSearch'
import type { Place } from './placeSearch'

type Status = 'idle' | 'loading' | 'success' | 'error'

export default function SearchPanel() {
  const [query, setQuery] = useState('')
  const [places, setPlaces] = useState<Place[]>([])
  const [status, setStatus] = useState<Status>('idle')
  const [saveMessage, setSaveMessage] = useState('')
  const [pending, setPending] = useState<Set<string>>(new Set())
  const pendingIds = useRef(new Set<string>())
  async function select(place: Place) {
    if (!canSave(place) || pendingIds.current.has(place.osm_id!)) return
    const identity = place.osm_id!
    pendingIds.current.add(identity)
    setPending(new Set(pendingIds.current))
    setSaveMessage(`Saving ${place.name}…`)
    try {
      const result = await savePlace(place)
      setSaveMessage(result.outcome === 'created'
        ? `Saved ${place.name}.` : `Already saved: ${place.name}.`)
    } catch {
      setSaveMessage(`Could not save ${place.name}. Select the restaurant again to retry.`)
    } finally {
      pendingIds.current.delete(identity)
      setPending(new Set(pendingIds.current))
    }
  }
  const request = useRef<AbortController | null>(null)
  useEffect(() => () => request.current?.abort(), [])

  function changeQuery(value: string) {
    request.current?.abort()
    setQuery(value)
    setPlaces([])
    setStatus('idle')
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    request.current?.abort()
    const controller = new AbortController()
    request.current = controller
    setPlaces([])
    if (!query.trim()) { setStatus('idle'); return }
    setStatus('loading')
    try {
      const results = await searchPlaces(query.trim(), controller.signal)
      if (controller.signal.aborted) return
      setPlaces(results)
      setStatus('success')
    } catch {
      if (!controller.signal.aborted) setStatus('error')
    }
  }

  return (
    <section className="search-panel" aria-label="Restaurant search">
      <div className="search-heading"><h1>Food Maps</h1><p>Find a restaurant by name</p></div>
      <form onSubmit={submit} className="search-form">
        <label htmlFor="restaurant-query" className="sr-only">Restaurant name</label>
        <input id="restaurant-query" type="search" value={query} maxLength={200}
          placeholder="Search restaurants" onChange={event => changeQuery(event.target.value)} />
        <button type="submit">Search</button>
      </form>
      <div role="status" aria-live="polite" aria-atomic="true">
        {status === 'loading' && <p className="search-message">Searching locations…</p>}
        {status === 'error' && <p className="search-message">Location search is unavailable. Please try again later.</p>}
        {status === 'success' && <p className="search-message">{places.length ? `${places.length} locations found` : 'No matching locations found'}</p>}
      </div>
      <p className="search-message" role="status" aria-live="polite" aria-atomic="true">{saveMessage}</p>
      {places.length > 0 && <ul className="search-results" aria-label="Search results">
        {places.map(place => <li key={place.display_name}>
          <button type="button" className="result-select"
            aria-label={`Save ${place.name || 'location'}: ${place.display_name}`}
            disabled={!canSave(place) || pending.has(place.osm_id!)}
            onClick={() => void select(place)}>
            {place.name && <strong>{place.name}</strong>}
            <span>{place.display_name}</span>
            {pending.has(place.osm_id!) && <span>Saving…</span>}
            {!canSave(place) && <span>Cannot save: location details are incomplete. Try another result or search.</span>}
          </button>
        </li>)}
      </ul>}
      <p className="search-credit">Search data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a></p>
    </section>
  )
}

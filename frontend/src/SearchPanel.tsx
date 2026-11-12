import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { searchPlaces } from './placeSearch'
import type { Place } from './placeSearch'

type Status = 'idle' | 'loading' | 'success' | 'error'

export default function SearchPanel() {
  const [query, setQuery] = useState('')
  const [places, setPlaces] = useState<Place[]>([])
  const [status, setStatus] = useState<Status>('idle')
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
      {places.length > 0 && <ul className="search-results" aria-label="Search results">
        {places.map(place => <li key={place.display_name}>
          {place.name && <strong>{place.name}</strong>}
          <span>{place.display_name}</span>
        </li>)}
      </ul>}
      <p className="search-credit">Search data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a></p>
    </section>
  )
}

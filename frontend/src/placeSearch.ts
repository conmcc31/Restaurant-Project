export type Place = { name: string; display_name: string; latitude: number | null; longitude: number | null; osm_id: string | null }

export async function searchPlaces(query: string, signal: AbortSignal): Promise<Place[]> {
  const response = await fetch(`/api/places/search?${new URLSearchParams({ q: query })}`, { signal })
  if (!response.ok) throw new Error('Search failed')
  return (await response.json() as Place[]).slice(0, 5)
}

export function canSave(place: Place): boolean {
  return Boolean(place.name.trim() && place.display_name.trim() && place.osm_id &&
    /^(node|way|relation)\/[1-9][0-9]*$/.test(place.osm_id) &&
    typeof place.latitude === 'number' && Number.isFinite(place.latitude) && Math.abs(place.latitude) <= 90 &&
    typeof place.longitude === 'number' && Number.isFinite(place.longitude) && Math.abs(place.longitude) <= 180)
}

export type SaveResult = {
  outcome: 'created' | 'already_saved'
  restaurant: { id: number; user_id: string; name: string; address: string; latitude: number; longitude: number; osm_id: string }
}

export async function savePlace(place: Place): Promise<SaveResult> {
  const response = await fetch('/api/restaurants', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: place.name, address: place.display_name,
      latitude: place.latitude, longitude: place.longitude, osm_id: place.osm_id }),
  })
  if (!response.ok) throw new Error('Save failed')
  return await response.json() as SaveResult
}

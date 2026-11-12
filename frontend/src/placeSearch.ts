export type Place = { name: string; display_name: string }

export async function searchPlaces(query: string, signal: AbortSignal): Promise<Place[]> {
  const response = await fetch(`/api/places/search?${new URLSearchParams({ q: query })}`, { signal })
  if (!response.ok) throw new Error('Search failed')
  return (await response.json() as Place[]).slice(0, 5)
}

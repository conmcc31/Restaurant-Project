import { act, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import App from './App'

vi.mock('./MapView', () => ({ default: () => <div aria-label="Boston map" /> }))
afterEach(() => vi.unstubAllGlobals())
function enter(query: string) { fireEvent.change(screen.getByRole('searchbox'), { target: { value: query } }) }
function submit() { fireEvent.submit(screen.getByRole('button', { name: 'Search' }).closest('form')!) }
function reply(data: unknown, ok = true) { return { ok, json: async () => data } }

test('searches only on submit, skips blanks, renders at most five results and clears them', async () => {
  const fetch = vi.fn().mockResolvedValue(reply(Array.from({ length: 7 }, (_, i) => ({ name: `Cafe ${i}`, display_name: `Cafe ${i}, Boston, Massachusetts`, latitude: 42.36, longitude: -71.05, osm_id: `node/${i + 1}` }))))
  vi.stubGlobal('fetch', fetch)
  render(<App />)
  expect(fetch).not.toHaveBeenCalled()
  submit()
  enter('   '); submit()
  expect(fetch).not.toHaveBeenCalled()
  enter('110 Grill')
  expect(fetch).not.toHaveBeenCalled()
  submit()
  expect(screen.getAllByRole('status')[0]).toHaveTextContent('Searching')
  expect(await screen.findAllByRole('listitem')).toHaveLength(5)
  expect(screen.getByText('Cafe 0, Boston, Massachusetts')).toBeInTheDocument()
  expect(fetch).toHaveBeenCalledTimes(1)
  expect(fetch.mock.calls[0][0]).toBe('/api/places/search?q=110+Grill')
  enter('')
  expect(screen.queryByRole('list')).not.toBeInTheDocument()
})

test('shows empty and failed searches, then recovers via the search button', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(reply([]))
    .mockResolvedValueOnce(reply({}, false))
    .mockResolvedValueOnce(reply([{ name: 'Cafe', display_name: 'Cafe, Boston', latitude: 42.36, longitude: -71.05, osm_id: 'node/123' }])))
  render(<App />)
  enter('Cafe'); submit()
  expect(await screen.findByText('No matching locations found')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'Search' }))
  expect(await screen.findByText(/search is unavailable/)).toBeInTheDocument()
  submit()
  expect(await screen.findByText('Cafe, Boston')).toBeInTheDocument()
})

test('ignores delayed responses after a newer query or clearing the field', async () => {
  let resolveOld!: (value: unknown) => void
  let resolveCleared!: (value: unknown) => void
  vi.stubGlobal('fetch', vi.fn().mockReturnValueOnce(new Promise(resolve => { resolveOld = resolve }))
    .mockResolvedValueOnce(reply([{ name: 'New', display_name: 'New, Boston', latitude: 42.36, longitude: -71.05, osm_id: 'node/123' }]))
    .mockReturnValueOnce(new Promise(resolve => { resolveCleared = resolve })))
  render(<App />)
  enter('Old'); submit()
  enter('New'); submit()
  expect(await screen.findByText('New, Boston')).toBeInTheDocument()
  await act(async () => resolveOld(reply([{ name: 'Old', display_name: 'Old, Boston', latitude: 42.36, longitude: -71.05, osm_id: 'node/123' }])))
  expect(screen.queryByText('Old, Boston')).not.toBeInTheDocument()
  enter('Pending'); submit()
  enter('')
  await act(async () => resolveCleared(reply([{ name: 'Pending', display_name: 'Pending, Boston', latitude: 42.36, longitude: -71.05, osm_id: 'node/123' }])))
  expect(screen.queryByRole('list')).not.toBeInTheDocument()
  expect(screen.getAllByRole('status')[0]).toBeEmptyDOMElement()
})

test('announces a network failure and keeps the form usable', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
  render(<App />)
  enter('Cafe'); submit()
  expect(await screen.findByText(/search is unavailable/)).toBeInTheDocument()
  expect(screen.getByRole('searchbox')).toBeEnabled()
  expect(screen.getByRole('button', { name: 'Search' })).toBeEnabled()
})

const cafe = { name: 'Cafe', display_name: 'Cafe, Boston', latitude: 42.36, longitude: -71.05, osm_id: 'node/123' }
const saved = (outcome = 'created') => reply({ outcome, restaurant: { ...cafe, address: cafe.display_name, id: 1, user_id: 'xyz123' } })

test('selection posts matching data, blocks pending repeat activation, and reports duplicates', async () => {
  let finish!: (value: unknown) => void
  const fetch = vi.fn().mockResolvedValueOnce(reply([cafe]))
    .mockReturnValueOnce(new Promise(resolve => { finish = resolve }))
    .mockResolvedValueOnce(saved('already_saved'))
  vi.stubGlobal('fetch', fetch)
  render(<App />)
  enter('Cafe'); submit()
  const button = await screen.findByRole('button', { name: 'Save Cafe: Cafe, Boston' })
  expect(button).toHaveAttribute('type', 'button')
  button.focus()
  expect(button).toHaveFocus()
  fireEvent.click(button)
  expect(screen.getByText('Saving Cafe…')).toBeInTheDocument()
  expect(button).toBeDisabled()
  fireEvent.click(button)
  expect(fetch).toHaveBeenCalledTimes(2)
  expect(fetch.mock.calls[1]).toEqual(['/api/restaurants', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: cafe.name, address: cafe.display_name, latitude: cafe.latitude, longitude: cafe.longitude, osm_id: cafe.osm_id }),
  }])
  expect(screen.queryByText('Saved Cafe.')).not.toBeInTheDocument()
  await act(async () => finish(saved()))
  expect(screen.getByText('Saved Cafe.')).toBeInTheDocument()
  fireEvent.click(button)
  expect(await screen.findByText('Already saved: Cafe.')).toBeInTheDocument()
})

test('save failure preserves retry and search usability', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(reply([cafe]))
    .mockResolvedValueOnce(reply({}, false)).mockResolvedValueOnce(saved()))
  render(<App />)
  enter('Cafe'); submit()
  const button = await screen.findByRole('button', { name: 'Save Cafe: Cafe, Boston' })
  fireEvent.click(button)
  expect(await screen.findByText(/Could not save Cafe/)).toBeInTheDocument()
  expect(button).toBeEnabled()
  expect(screen.getByRole('searchbox')).toBeEnabled()
  fireEvent.click(button)
  expect(await screen.findByText('Saved Cafe.')).toBeInTheDocument()
})

test('late saves identify the original restaurant after searching again', async () => {
  let finish!: (value: unknown) => void
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(reply([cafe]))
    .mockReturnValueOnce(new Promise(resolve => { finish = resolve }))
    .mockResolvedValueOnce(reply([{ ...cafe, name: 'Other', display_name: 'Other, Boston', osm_id: 'way/456' }])))
  render(<App />)
  enter('Cafe'); submit()
  fireEvent.click(await screen.findByRole('button', { name: 'Save Cafe: Cafe, Boston' }))
  enter('Other'); submit()
  const other = await screen.findByRole('button', { name: 'Save Other: Other, Boston' })
  await act(async () => finish(saved()))
  expect(screen.getByText('Saved Cafe.')).toBeInTheDocument()
  expect(other).toBeEnabled()
  expect(other).not.toHaveTextContent('Saved')
})

test('incomplete results remain readable and cannot be saved', async () => {
  const fetch = vi.fn().mockResolvedValue(reply([{ ...cafe, osm_id: null }]))
  vi.stubGlobal('fetch', fetch)
  render(<App />)
  enter('Cafe'); submit()
  const button = await screen.findByRole('button', { name: 'Save Cafe: Cafe, Boston' })
  expect(button).toBeDisabled()
  fireEvent.click(button)
  expect(fetch).toHaveBeenCalledTimes(1)
})

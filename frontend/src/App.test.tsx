import { act, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import App from './App'

vi.mock('./MapView', () => ({ default: () => <div aria-label="Boston map" /> }))
afterEach(() => vi.unstubAllGlobals())
function enter(query: string) { fireEvent.change(screen.getByRole('searchbox'), { target: { value: query } }) }
function submit() { fireEvent.submit(screen.getByRole('button', { name: 'Search' }).closest('form')!) }
function reply(data: unknown, ok = true) { return { ok, json: async () => data } }

test('searches only on submit, skips blanks, renders at most five results and clears them', async () => {
  const fetch = vi.fn().mockResolvedValue(reply(Array.from({ length: 7 }, (_, i) => ({ name: `Cafe ${i}`, display_name: `Cafe ${i}, Boston, Massachusetts` }))))
  vi.stubGlobal('fetch', fetch)
  render(<App />)
  expect(fetch).not.toHaveBeenCalled()
  submit()
  enter('   '); submit()
  expect(fetch).not.toHaveBeenCalled()
  enter('110 Grill')
  expect(fetch).not.toHaveBeenCalled()
  submit()
  expect(screen.getByRole('status')).toHaveTextContent('Searching')
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
    .mockResolvedValueOnce(reply([{ name: 'Cafe', display_name: 'Cafe, Boston' }])))
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
    .mockResolvedValueOnce(reply([{ name: 'New', display_name: 'New, Boston' }]))
    .mockReturnValueOnce(new Promise(resolve => { resolveCleared = resolve })))
  render(<App />)
  enter('Old'); submit()
  enter('New'); submit()
  expect(await screen.findByText('New, Boston')).toBeInTheDocument()
  await act(async () => resolveOld(reply([{ name: 'Old', display_name: 'Old, Boston' }])))
  expect(screen.queryByText('Old, Boston')).not.toBeInTheDocument()
  enter('Pending'); submit()
  enter('')
  await act(async () => resolveCleared(reply([{ name: 'Pending', display_name: 'Pending, Boston' }])))
  expect(screen.queryByRole('list')).not.toBeInTheDocument()
  expect(screen.getByRole('status')).toBeEmptyDOMElement()
})

test('announces a network failure and keeps the form usable', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
  render(<App />)
  enter('Cafe'); submit()
  expect(await screen.findByText(/search is unavailable/)).toBeInTheDocument()
  expect(screen.getByRole('searchbox')).toBeEnabled()
  expect(screen.getByRole('button', { name: 'Search' })).toBeEnabled()
})

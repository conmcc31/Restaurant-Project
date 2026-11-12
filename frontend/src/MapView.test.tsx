import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import MapView from './MapView'

test('mounts the real Leaflet map with attribution and zoom controls, without markers', () => {
  const { container } = render(<MapView />)
  expect(container.querySelector('.leaflet-container')).toBeInTheDocument()
  expect(screen.getByRole('link', { name: 'OpenStreetMap' })).toHaveAttribute('href', 'https://www.openstreetmap.org/copyright')
  expect(screen.getByRole('button', { name: 'Zoom in' })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Zoom out' })).toBeInTheDocument()
  expect(container.querySelector('.leaflet-marker-icon')).not.toBeInTheDocument()
})

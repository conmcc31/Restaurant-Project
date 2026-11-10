import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import App from './App'

test('renders the setup starter page', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: 'Food Maps' })).toBeInTheDocument()
  expect(screen.getByText(/Local development starter/)).toBeInTheDocument()
})

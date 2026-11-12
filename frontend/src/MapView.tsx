import { MapContainer, TileLayer, ZoomControl } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

export default function MapView() {
  return (
    <MapContainer center={[42.3601, -71.0589]} zoom={13} zoomControl={false}
      className="map" aria-label="Map centered on Boston, Massachusetts">
      <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' />
      <ZoomControl position="bottomright" />
    </MapContainer>
  )
}

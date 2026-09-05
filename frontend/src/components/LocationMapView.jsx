import React, { useState, useEffect } from 'react';
import { MapPin, X } from 'lucide-react';

/**
 * LocationMapView - Shows suspect locations on Google Maps
 * Displays entities with location data as markers
 */
export default function LocationMapView({ graphData, selectedNode, onSelectNode }) {
  const mapRef = React.useRef(null);
  const [map, setMap] = useState(null);
  const [markers, setMarkers] = useState([]);
  const [apiLoaded, setApiLoaded] = useState(false);

  // Check if Google Maps API is loaded
  useEffect(() => {
    if (window.google && window.google.maps) {
      setApiLoaded(true);
    } else {
      setApiLoaded(false);
    }
  }, []);

  // Initialize Google Map
  useEffect(() => {
    if (!mapRef.current || !apiLoaded) return;

    try {
      // Create map centered on India
      const newMap = new window.google.maps.Map(mapRef.current, {
        zoom: 5,
        center: { lat: 20.5937, lng: 78.9629 },
        mapTypeId: 'roadmap',
        styles: [
          { elementType: 'geometry', stylers: [{ color: '#1a1a1a' }] },
          { elementType: 'labels.text.stroke', stylers: [{ color: '#1a1a1a' }] },
          { elementType: 'labels.text.fill', stylers: [{ color: '#e2e8f0' }] },
          { featureType: 'administrative.locality', elementType: 'labels.text.fill', stylers: [{ color: '#94a3b8' }] },
          { featureType: 'poi', stylers: [{ visibility: 'off' }] },
          { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#2e3c54' }] },
          { featureType: 'road', elementType: 'geometry.stroke', stylers: [{ color: '#1a1a1a' }] },
          { featureType: 'road', elementType: 'labels.text.fill', stylers: [{ color: '#94a3b8' }] },
          { featureType: 'water', elementType: 'geometry', stylers: [{ color: '#0a0f18' }] },
          { featureType: 'water', elementType: 'labels.text.fill', stylers: [{ color: '#94a3b8' }] },
        ],
      });

      setMap(newMap);
    } catch (e) {
      console.error('Google Maps initialization failed:', e);
      setApiLoaded(false);
    }
  }, [apiLoaded]);

  // Demo locations (Indian cities for suspects)
  const DEMO_LOCATIONS = {
    'Mumbai': { lat: 19.0760, lng: 72.8777, color: '#ef4444' },
    'Delhi': { lat: 28.7041, lng: 77.1025, color: '#3b82f6' },
    'Bangalore': { lat: 12.9716, lng: 77.5946, color: '#10b981' },
    'Hyderabad': { lat: 17.3850, lng: 78.4867, color: '#f59e0b' },
    'Kolkata': { lat: 22.5726, lng: 88.3639, color: '#a855f7' },
    'Chennai': { lat: 13.0827, lng: 80.2707, color: '#ec4899' },
  };

  // Add markers for location nodes
  useEffect(() => {
    if (!map) return;

    // Clear existing markers
    markers.forEach(m => m.setMap(null));
    setMarkers([]);

    const newMarkers = [];
    let hasRealLocations = false;

    // Check if we have real location data in graph
    if (graphData && graphData.nodes) {
      graphData.nodes.forEach(node => {
        if (node.type === 'Location' && node.metadata) {
          const lat = node.metadata.latitude;
          const lng = node.metadata.longitude;

          if (lat && lng) {
            hasRealLocations = true;
            const marker = new window.google.maps.Marker({
              position: { lat, lng },
              map,
              title: node.label,
              icon: {
                path: window.google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: '#a855f7',
                fillOpacity: 0.8,
                strokeColor: '#ffffff',
                strokeWeight: 2,
              },
            });

            marker.addListener('click', () => {
              onSelectNode({
                id: node.id,
                name: node.label,
                type: node.type,
                metadata: node.metadata,
              });
            });

            newMarkers.push(marker);
          }
        }
      });
    }

    // If no real locations, add demo markers for Indian cities
    if (!hasRealLocations && graphData && graphData.nodes && graphData.nodes.length > 0) {
      const locationNames = Object.keys(DEMO_LOCATIONS);
      let locIndex = 0;

      // Add markers for the first 5-6 suspects at different cities
      graphData.nodes.forEach((node, idx) => {
        if (idx < 6 && locIndex < locationNames.length) {
          const cityName = locationNames[locIndex];
          const locData = DEMO_LOCATIONS[cityName];

          const marker = new window.google.maps.Marker({
            position: { lat: locData.lat, lng: locData.lng },
            map,
            title: `${node.label} (${cityName})`,
            icon: {
              path: window.google.maps.SymbolPath.CIRCLE,
              scale: 12,
              fillColor: locData.color,
              fillOpacity: 0.85,
              strokeColor: '#ffffff',
              strokeWeight: 2,
            },
          });

          marker.addListener('click', () => {
            onSelectNode({
              id: node.id,
              name: `${node.label} (${cityName})`,
              type: 'Location',
              metadata: {
                latitude: locData.lat,
                longitude: locData.lng,
                city: cityName,
                state: 'India',
              },
            });
          });

          newMarkers.push(marker);
          locIndex++;
        }
      });
    }

    setMarkers(newMarkers);

    // Fit bounds if markers exist
    if (newMarkers.length > 0) {
      const bounds = new window.google.maps.LatLngBounds();
      newMarkers.forEach(m => bounds.extend(m.getPosition()));
      map.fitBounds(bounds, 50);
    }
  }, [map, graphData]);

  // Highlight selected node on map
  useEffect(() => {
    if (!selectedNode || !map) return;

    if (selectedNode.metadata?.latitude && selectedNode.metadata?.longitude) {
      map.panTo({
        lat: selectedNode.metadata.latitude,
        lng: selectedNode.metadata.longitude,
      });
      map.setZoom(8);
    }
  }, [selectedNode, map]);

  if (!apiLoaded) {
    return (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#0a0f18',
          flexDirection: 'column',
          gap: 16,
        }}
      >
        <MapPin size={48} color="#94a3b8" style={{ opacity: 0.5 }} />
        <div style={{ textAlign: 'center', color: '#94a3b8' }}>
          <p style={{ marginBottom: 8 }}>Google Maps API not loaded</p>
          <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
            Add a valid Google Maps API key to index.html to enable map view
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <div
        ref={mapRef}
        style={{
          width: '100%',
          height: '100%',
          position: 'absolute',
          top: 0,
          left: 0,
        }}
      />

      {/* Info Panel */}
      {selectedNode && selectedNode.type === 'Location' && (
        <div
          style={{
            position: 'absolute',
            top: 20,
            right: 20,
            background: 'rgba(19, 27, 44, 0.95)',
            border: '1px solid #2e3c54',
            borderRadius: 8,
            padding: 16,
            maxWidth: 300,
            zIndex: 10,
            backdropFilter: 'blur(12px)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <MapPin size={18} color="#a855f7" />
              <span style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                Location
              </span>
            </div>
            <button
              onClick={() => onSelectNode(null)}
              style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#94a3b8' }}
            >
              <X size={16} />
            </button>
          </div>

          <h3 style={{ fontSize: '1.1rem', color: '#fff', marginBottom: 12 }}>
            {selectedNode.name}
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.85rem' }}>
            <div>
              <span style={{ color: '#94a3b8' }}>Latitude:</span>
              <span style={{ color: '#10b981', marginLeft: 8 }}>
                {selectedNode.metadata?.latitude?.toFixed(4)}
              </span>
            </div>
            <div>
              <span style={{ color: '#94a3b8' }}>Longitude:</span>
              <span style={{ color: '#10b981', marginLeft: 8 }}>
                {selectedNode.metadata?.longitude?.toFixed(4)}
              </span>
            </div>
            {selectedNode.metadata?.city && (
              <div>
                <span style={{ color: '#94a3b8' }}>City:</span>
                <span style={{ color: '#e2e8f0', marginLeft: 8 }}>
                  {selectedNode.metadata.city}
                </span>
              </div>
            )}
            {selectedNode.metadata?.state && (
              <div>
                <span style={{ color: '#94a3b8' }}>State:</span>
                <span style={{ color: '#e2e8f0', marginLeft: 8 }}>
                  {selectedNode.metadata.state}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Demo Info */}
      {!selectedNode && (
        <div
          style={{
            position: 'absolute',
            bottom: 20,
            left: 20,
            background: 'rgba(19, 27, 44, 0.9)',
            border: '1px solid #2e3c54',
            borderRadius: 8,
            padding: 12,
            fontSize: '0.8rem',
            color: '#94a3b8',
            maxWidth: 280,
            zIndex: 5,
          }}
        >
          <p style={{ margin: '0 0 8px 0', fontWeight: 'bold', color: '#e2e8f0' }}>Demo Mode</p>
          <p style={{ margin: 0 }}>
            Suspects are placed at major Indian cities for demonstration. Click on any marker to see details.
          </p>
        </div>
      )}
    </div>
  );
}

import React, { useRef, useEffect, useState, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { ZoomIn, ZoomOut, Maximize2, Filter, X, User, Phone, Car, Landmark, MapPin, FileText } from 'lucide-react';
import QueryBar from './QueryBar';

const ENTITY_COLORS = {
  Person: '#ef4444',       // Crimson Red
  Phone: '#06b6d4',        // Cyan
  Vehicle: '#f59e0b',      // Amber
  BankAccount: '#10b981',  // Emerald Green
  Location: '#a855f7',     // Purple
  Case: '#3b82f6',         // Blue
  Organization: '#ec4899', // Pink
  Crime: '#dc2626'         // Dark Red
};

export default function GraphCanvas({ graphData, onSelectNode, selectedNode }) {
  const containerRef = useRef(null);
  const fgRef = useRef(null);

  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [filterType, setFilterType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Update canvas dimensions on container resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Format data for ForceGraph2D
  const formattedData = useMemo(() => {
    if (!graphData || !graphData.nodes) {
      return { nodes: [], links: [] };
    }

    let nodes = graphData.nodes.map(n => ({
      id: n.id,
      name: n.label || n.id,
      type: n.type || 'Unknown',
      val: n.type === 'Person' ? 8 : (n.type === 'BankAccount' ? 6 : 4),
      color: ENTITY_COLORS[n.type] || '#94a3b8',
      metadata: n.metadata || {}
    }));

    let links = graphData.edges.map(e => ({
      source: e.source,
      target: e.target,
      label: e.label || '',
      type: e.type || '',
      weight: e.weight || 1
    }));

    // Apply Filter by Type
    if (filterType !== 'ALL') {
      const allowedNodeIds = new Set(nodes.filter(n => n.type === filterType).map(n => n.id));
      nodes = nodes.filter(n => allowedNodeIds.has(n.id));
      links = links.filter(l => allowedNodeIds.has(l.source) && allowedNodeIds.has(l.target));
    }

    // Apply Search Query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      nodes = nodes.map(n => ({
        ...n,
        isHighlighted: n.name.toLowerCase().includes(q) || n.id.toLowerCase().includes(q)
      }));
    }

    return { nodes, links };
  }, [graphData, filterType, searchQuery]);

  // Zoom controls
  const handleZoomIn = () => {
    if (fgRef.current) fgRef.current.zoom(fgRef.current.zoom() * 1.3, 400);
  };

  const handleZoomOut = () => {
    if (fgRef.current) fgRef.current.zoom(fgRef.current.zoom() / 1.3, 400);
  };

  const handleZoomReset = () => {
    if (fgRef.current) fgRef.current.zoomToFit(400, 50);
  };

  const getNodeIcon = (type) => {
    switch (type) {
      case 'Person': return <User size={16} color="#ef4444" />;
      case 'Phone': return <Phone size={16} color="#06b6d4" />;
      case 'Vehicle': return <Car size={16} color="#f59e0b" />;
      case 'BankAccount': return <Landmark size={16} color="#10b981" />;
      case 'Location': return <MapPin size={16} color="#a855f7" />;
      default: return <FileText size={16} color="#3b82f6" />;
    }
  };

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden' }}>
      {/* Top Floating Controls Bar */}
      <div style={{
        position: 'absolute',
        top: 16,
        left: 16,
        zIndex: 10,
        display: 'flex',
        gap: 8,
        background: 'rgba(19, 27, 44, 0.85)',
        backdropFilter: 'blur(8px)',
        padding: '8px 12px',
        borderRadius: 8,
        border: '1px solid #2e3c54',
        alignItems: 'center'
      }}>
        {/* Search Input */}
        <input
          type="text"
          placeholder="Search node / phone / plate..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            background: '#0a0f18',
            border: '1px solid #2e3c54',
            color: '#fff',
            padding: '6px 12px',
            borderRadius: 4,
            fontSize: '0.85rem',
            outline: 'none',
            width: 220
          }}
        />

        {/* Entity Type Filter */}
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          style={{
            background: '#0a0f18',
            border: '1px solid #2e3c54',
            color: '#e2e8f0',
            padding: '6px 10px',
            borderRadius: 4,
            fontSize: '0.85rem',
            outline: 'none',
            cursor: 'pointer'
          }}
        >
          <option value="ALL">All Types</option>
          <option value="Person">Suspects (Person)</option>
          <option value="Phone">Phones</option>
          <option value="Vehicle">Vehicles</option>
          <option value="BankAccount">Bank Accounts</option>
          <option value="Location">Locations</option>
        </select>
      </div>

      {/* Floating Zoom Controls */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        right: 20,
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
        background: 'rgba(19, 27, 44, 0.85)',
        backdropFilter: 'blur(8px)',
        padding: 6,
        borderRadius: 8,
        border: '1px solid #2e3c54'
      }}>
        <button onClick={handleZoomIn} style={controlBtnStyle} title="Zoom In">
          <ZoomIn size={18} color="#e2e8f0" />
        </button>
        <button onClick={handleZoomOut} style={controlBtnStyle} title="Zoom Out">
          <ZoomOut size={18} color="#e2e8f0" />
        </button>
        <button onClick={handleZoomReset} style={controlBtnStyle} title="Reset View">
          <Maximize2 size={18} color="#e2e8f0" />
        </button>
      </div>

      {/* Legend */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        left: 20,
        zIndex: 10,
        background: 'rgba(19, 27, 44, 0.85)',
        backdropFilter: 'blur(8px)',
        padding: '10px 14px',
        borderRadius: 8,
        border: '1px solid #2e3c54',
        fontSize: '0.75rem',
        color: '#94a3b8',
        display: 'flex',
        flexDirection: 'column',
        gap: 6
      }}>
        <div style={{ fontWeight: 'bold', color: '#e2e8f0', marginBottom: 2 }}>Legend</div>
        {Object.entries(ENTITY_COLORS).slice(0, 5).map(([type, color]) => (
          <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: color }} />
            <span>{type}</span>
          </div>
        ))}
      </div>

      {/* Force Directed Graph */}
      <ForceGraph2D
        ref={fgRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={formattedData}
        backgroundColor="#0a0f18"
        nodeRelSize={4}
        nodeColor={(node) => node.color}
        nodeLabel={(node) => `${node.type}: ${node.name}`}
        linkColor={() => 'rgba(148, 163, 184, 0.25)'}
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.005}
        linkDirectionalParticleWidth={2}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        onNodeClick={(node) => {
          if (onSelectNode) onSelectNode(node);
        }}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12 / globalScale;
          const radius = node.type === 'Person' ? 6 : 4.5;

          // Draw outer glow if highlighted
          if (node.isHighlighted || (selectedNode && selectedNode.id === node.id)) {
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius + 3, 0, 2 * Math.PI, false);
            ctx.fillStyle = 'rgba(0, 240, 255, 0.4)';
            ctx.fill();
            ctx.lineWidth = 1.5;
            ctx.strokeStyle = '#00f0ff';
            ctx.stroke();
          }

          // Node Circle
          ctx.beginPath();
          ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
          ctx.fillStyle = node.color;
          ctx.fill();

          // Label text
          if (globalScale > 1.2 || node.type === 'Person' || node.isHighlighted) {
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#ffffff';
            ctx.fillText(label, node.x, node.y + radius + fontSize + 2);
          }
        }}
      />

      {/* Selected Node Inspector Drawer */}
      {selectedNode && (
        <div style={{
          position: 'absolute',
          top: 16,
          right: 16,
          width: 300,
          background: 'rgba(19, 27, 44, 0.95)',
          backdropFilter: 'blur(12px)',
          border: '1px solid #2e3c54',
          borderRadius: 8,
          padding: 16,
          zIndex: 20,
          boxShadow: '0 10px 25px -5px rgba(0,0,0,0.5)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {getNodeIcon(selectedNode.type)}
              <span style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                {selectedNode.type}
              </span>
            </div>
            <button
              onClick={() => onSelectNode(null)}
              style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#94a3b8' }}
            >
              <X size={18} />
            </button>
          </div>

          <h3 style={{ fontSize: '1.1rem', color: '#fff', marginBottom: 12 }}>
            {selectedNode.name || selectedNode.id}
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #2e3c54', paddingBottom: 6 }}>
              <span style={{ color: '#94a3b8' }}>Entity ID</span>
              <span style={{ color: '#e2e8f0', fontFamily: 'monospace' }}>{selectedNode.id}</span>
            </div>

            {selectedNode.metadata?.aliases && selectedNode.metadata.aliases.length > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #2e3c54', paddingBottom: 6 }}>
                <span style={{ color: '#94a3b8' }}>Aliases</span>
                <span style={{ color: '#00f0ff' }}>{selectedNode.metadata.aliases.join(', ')}</span>
              </div>
            )}

            {selectedNode.metadata?.confidence && (
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #2e3c54', paddingBottom: 6 }}>
                <span style={{ color: '#94a3b8' }}>Confidence</span>
                <span style={{ color: '#10b981' }}>{(selectedNode.metadata.confidence * 100).toFixed(0)}%</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Natural Language Query Bar */}
      <QueryBar graphData={graphData} onHighlightPath={null} />
    </div>
  );
}

const controlBtnStyle = {
  background: '#0a0f18',
  border: '1px solid #2e3c54',
  borderRadius: 4,
  padding: 8,
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'background 0.2s'
};

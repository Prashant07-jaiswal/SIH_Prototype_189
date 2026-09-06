import React, { useState, useEffect } from 'react';
import { Network, Database, Users, Activity, Shield, AlertTriangle, RefreshCw, UploadCloud } from 'lucide-react';
import * as api from './services/api';
import GraphCanvas from './components/GraphCanvas';
import UploadModal from './components/UploadModal';
import './index.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [dataLoaded, setDataLoaded] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  // State for analytics and graph
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [keyPlayers, setKeyPlayers] = useState([]);
  const [communities, setCommunities] = useState([]);
  const [graphStats, setGraphStats] = useState({ nodes: 0, edges: 0 });
  const [selectedNode, setSelectedNode] = useState(null);

  // Fetch data on mount
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // 1. Fetch current graph
      try {
        const graphRes = await api.getGraphData();
        if (graphRes.data && graphRes.data.nodes && graphRes.data.nodes.length > 0) {
          setGraphData(graphRes.data);
          setGraphStats({
            nodes: graphRes.data.node_count || graphRes.data.nodes.length,
            edges: graphRes.data.edge_count || graphRes.data.edges.length,
          });
          setDataLoaded(true);
        } else {
          setDataLoaded(false);
          setLoading(false);
          return;
        }
      } catch (e) {
        setDataLoaded(false);
        setLoading(false);
        return;
      }

      // 2. Fetch Key Players
      try {
        const playersRes = await api.getKeyPlayers();
        if (playersRes.data && playersRes.data.key_players) {
          setKeyPlayers(playersRes.data.key_players.slice(0, 5));
        }
      } catch (err) {
        console.warn("Key players not ready yet", err);
      }

      // 3. Fetch Communities
      try {
        const commRes = await api.getCommunities();
        if (commRes.data && commRes.data.communities) {
          setCommunities(commRes.data.communities.slice(0, 4));
        }
      } catch (err) {
        console.warn("Communities not ready yet", err);
      }

    } catch (error) {
      console.error("Error fetching dashboard data", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunIngestion = async () => {
    try {
      setLoading(true);
      await api.runIngestion();
      await fetchDashboardData();
    } catch (error) {
      console.error("Error running ingestion", error);
      alert("Error processing data: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSelectKeyPlayer = (player) => {
    // Find node in graph data and highlight/select it
    const foundNode = graphData.nodes?.find(n => n.id === player.entity_id || n.label === player.entity_name);
    if (foundNode) {
      setSelectedNode({
        id: foundNode.id,
        name: foundNode.label,
        type: foundNode.type,
        metadata: {
          ...foundNode.metadata,
          aliases: player.aliases,
          risk_score: player.risk_score,
          connections: player.connections
        }
      });
    }
  };

  return (
    <div className="app-container">
      {/* Top Navigation Bar */}
      <header className="navbar">
        <div className="brand">
          <Shield color="#00f0ff" size={28} />
          <span className="brand-title">Criminal Network Intelligence</span>
        </div>

        <div className="action-bar">
          <button
            className="btn-primary"
            style={{ padding: '8px 16px', fontSize: '0.85rem', backgroundColor: '#1e293b', border: '1px solid #334155' }}
            onClick={fetchDashboardData}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} /> Refresh Graph
          </button>

          <button
            className="btn-primary"
            style={{ padding: '8px 16px', fontSize: '0.85rem', backgroundColor: '#6d28d9' }}
            onClick={() => setShowUpload(true)}
            disabled={loading}
          >
            <UploadCloud size={16} /> Upload Evidence
          </button>

          <button
            className="btn-primary"
            style={{ padding: '8px 16px', fontSize: '0.85rem', backgroundColor: '#3b82f6' }}
            onClick={handleRunIngestion}
            disabled={loading}
          >
            <Database size={16} /> Re-Ingest Data
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">

        {/* Left Analytics Side Panel */}
        <aside className="sidebar">
          {/* Section 1: Overview Stats */}
          <div className="sidebar-section">
            <h2 className="section-title">
              <Database size={18} /> Network Overview
            </h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{graphStats.nodes}</div>
                <div className="stat-label">Total Entities</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{graphStats.edges}</div>
                <div className="stat-label">Connections</div>
              </div>
            </div>
          </div>

          {/* Section 2: Key Players (Ranked Suspects) */}
          <div className="sidebar-section">
            <h2 className="section-title">
              <AlertTriangle size={18} color="#ef4444" /> High Risk Subjects
            </h2>
            {keyPlayers.length > 0 ? (
              <div className="player-list">
                {keyPlayers.map((player, idx) => (
                  <div
                    key={idx}
                    className="player-item"
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleSelectKeyPlayer(player)}
                  >
                    <div className="player-info">
                      <h4>{player.entity_name}</h4>
                      <p>{player.connections} Connections • Rank #{player.rank || idx + 1}</p>
                    </div>
                    <div className="risk-badge">
                      {(player.risk_score * 10).toFixed(1)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No high risk suspects loaded.</p>
            )}
          </div>

          {/* Section 3: Communities & Gangs */}
          <div className="sidebar-section" style={{ borderBottom: 'none' }}>
            <h2 className="section-title">
              <Users size={18} color="#f59e0b" /> Detected Syndicates
            </h2>
            {communities.length > 0 ? (
              <div className="player-list">
                {communities.map((comm, idx) => (
                  <div key={idx} className="player-item" style={{ borderLeftColor: '#f59e0b' }}>
                    <div className="player-info">
                      <h4>Syndicate #{comm.id}</h4>
                      <p>{comm.member_count} Members identified</p>
                    </div>
                    <div className="risk-badge" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' }}>
                      {comm.cohesion_score.toFixed(2)} Cohesion
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No syndicates detected.</p>
            )}
          </div>
        </aside>

        {/* Center Canvas Area */}
        <section className="graph-container">
          {!dataLoaded ? (
            <div className="empty-state">
              <Network size={64} color="#3b82f6" style={{ opacity: 0.5, marginBottom: '20px' }} />
              <h2 style={{ marginBottom: '10px' }}>No Network Data Loaded</h2>
              <p style={{ color: '#94a3b8', marginBottom: '24px' }}>
                Run the multi-source pipeline to extract FIRs, match CDR calls, and detect bank anomalies.
              </p>
              <button
                className="btn-primary"
                onClick={handleRunIngestion}
                disabled={loading}
                style={{ margin: '0 auto', opacity: loading ? 0.7 : 1 }}
              >
                {loading ? <Activity size={20} className="animate-spin" /> : <Database size={20} />}
                {loading ? 'Analyzing Intelligence Data...' : 'Run Pipeline & Ingest'}
              </button>
            </div>
          ) : (
            <GraphCanvas
              graphData={graphData}
              selectedNode={selectedNode}
              onSelectNode={setSelectedNode}
            />
          )}
        </section>

      </main>

      {/* Upload Modal */}
      {showUpload && (
        <UploadModal
          isOpen={showUpload}
          onClose={() => setShowUpload(false)}
          onRefresh={fetchDashboardData}
        />
      )}
    </div>
  );
}

export default App;

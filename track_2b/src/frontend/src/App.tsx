import React, { useState, useEffect } from 'react';
import {
  Shield,
  Radio,
  FileText,
  Mic,
  AlertTriangle,
  CheckCircle,
  Download,
  RefreshCw,
  PlusCircle,
  Lock,
  Edit2,
  XCircle,
} from 'lucide-react';

interface SourceReport {
  report_id: string;
  incident_id: string;
  modality: 'text' | 'image_document' | 'voice_audio';
  language: 'de' | 'fr' | 'it' | 'en' | 'und';
  author_role: string;
  received_at: string;
  source_channel: string;
  reliability_tier: string;
  raw_content: string;
  metadata?: Record<string, any>;
}

interface ExtractedClaim {
  claim_id: string;
  incident_id: string;
  source_id: string;
  field: string;
  normalized_value: string;
  original_value: string;
  evidence_pointer: string;
  language: string;
  confidence: number;
  extraction_status: string;
  operator_status: 'unreviewed' | 'confirmed' | 'edited' | 'rejected';
  operator_edited_value?: string;
  model_name: string;
  timestamp: string;
}

interface ClaimCluster {
  cluster_id: string;
  field: string;
  status: 'corroborated' | 'conflict' | 'single_source' | 'missing';
  claims: ExtractedClaim[];
  reconciled_value?: string;
  conflict_explanation?: string;
  operator_resolution?: string;
  is_critical_field: boolean;
}

interface SituationBrief {
  incident_id: string;
  title: string;
  executive_summary: string;
  confirmed_facts: Record<string, string>;
  unresolved_conflicts: string[];
  critical_missing_fields: string[];
  recommended_priorities: string[];
  multilingual_summaries: Record<string, string>;
  generated_at: string;
  model_name: string;
  approved_by_operator: boolean;
  operator_notes?: string;
}

interface Incident {
  incident_id: string;
  title: string;
  preset_id?: string;
  status: string;
  deployment_mode: string;
  created_at: string;
  updated_at: string;
  sources: SourceReport[];
  claims: ExtractedClaim[];
  clusters: ClaimCluster[];
  brief?: SituationBrief;
  audit_trail: any[];
}

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [, setIncidents] = useState<Incident[]>([]);
  const [activeIncident, setActiveIncident] = useState<Incident | null>(null);
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'de' | 'fr' | 'it'>('en');
  const [loading, setLoading] = useState<boolean>(false);
  const [auditStatus, setAuditStatus] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState<boolean>(false);

  // New report form state
  const [newReportModality, setNewReportModality] = useState<'text' | 'image_document' | 'voice_audio'>('text');
  const [newReportLang, setNewReportLang] = useState<'de' | 'fr' | 'it' | 'en'>('de');
  const [newReportRole, setNewReportRole] = useState<string>('First Responder Field Unit');
  const [newReportContent, setNewReportContent] = useState<string>('');

  // Initial load
  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/incidents`);
      if (res.ok) {
        const data: Incident[] = await res.json();
        setIncidents(data);
        if (data.length > 0) {
          setActiveIncident(data[0]);
          if (data[0].sources.length > 0) {
            setSelectedSourceId(data[0].sources[0].report_id);
          }
        }
      }
    } catch (err) {
      console.error('Failed to fetch incidents', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPreset = async (presetId: string) => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/presets/${presetId}/load`, { method: 'POST' });
      if (res.ok) {
        const updated: Incident = await res.json();
        setActiveIncident(updated);
        if (updated.sources.length > 0) {
          setSelectedSourceId(updated.sources[0].report_id);
        }
      }
    } catch (err) {
      console.error('Failed to load preset', err);
    } finally {
      setLoading(false);
    }
  };

  const handleProcessPipeline = async () => {
    if (!activeIncident) return;
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/incidents/${activeIncident.incident_id}/process`, {
        method: 'POST',
      });
      if (res.ok) {
        const updated: Incident = await res.json();
        setActiveIncident(updated);
      }
    } catch (err) {
      console.error('Failed to process pipeline', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOperatorAction = async (payload: {
    claim_id?: string;
    cluster_id?: string;
    action: string;
    new_value?: string;
  }) => {
    if (!activeIncident) return;
    try {
      const res = await fetch(`${API_BASE}/api/incidents/${activeIncident.incident_id}/operator-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...payload,
          operator_id: 'OP-SWISS-01',
        }),
      });
      if (res.ok) {
        const updated: Incident = await res.json();
        setActiveIncident(updated);
      }
    } catch (err) {
      console.error('Operator action failed', err);
    }
  };

  const handleApproveBrief = async () => {
    if (!activeIncident) return;
    try {
      const res = await fetch(`${API_BASE}/api/incidents/${activeIncident.incident_id}/approve-brief`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approved: true,
          operator_notes: 'Verified against cantonal emergency dispatch standards.',
          operator_id: 'OP-COMMANDER-URI',
        }),
      });
      if (res.ok) {
        const updated: Incident = await res.json();
        setActiveIncident(updated);
      }
    } catch (err) {
      console.error('Brief approval failed', err);
    }
  };

  const handleExportBundle = async () => {
    if (!activeIncident) return;
    try {
      const res = await fetch(`${API_BASE}/api/incidents/${activeIncident.incident_id}/export`);
      if (res.ok) {
        const bundle = await res.json();
        const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `RelayZero_Export_${activeIncident.incident_id}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('Export failed', err);
    }
  };

  const handleVerifyAudit = async () => {
    if (!activeIncident) return;
    try {
      const res = await fetch(`${API_BASE}/api/incidents/${activeIncident.incident_id}/audit-verify`);
      if (res.ok) {
        const data = await res.json();
        setAuditStatus(data.chain_intact ? `✓ SHA-256 Chain Intact (${data.entries_count} blocks)` : '✗ Audit Corrupted');
        setTimeout(() => setAuditStatus(null), 4000);
      }
    } catch (err) {
      console.error('Audit verification failed', err);
    }
  };

  const handleAddReportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeIncident || !newReportContent.trim()) return;
    try {
      const newReport: SourceReport = {
        report_id: `SRC-CUSTOM-${Date.now().toString().slice(-4)}`,
        incident_id: activeIncident.incident_id,
        modality: newReportModality,
        language: newReportLang,
        author_role: newReportRole,
        received_at: new Date().toISOString(),
        source_channel: 'Local Ingestion Terminal',
        reliability_tier: 'Manual Operator Entry',
        raw_content: newReportContent,
      };
      const res = await fetch(`${API_BASE}/api/incidents/${activeIncident.incident_id}/reports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newReport),
      });
      if (res.ok) {
        const updated: Incident = await res.json();
        setActiveIncident(updated);
        setSelectedSourceId(newReport.report_id);
        setShowAddModal(false);
        setNewReportContent('');
      }
    } catch (err) {
      console.error('Failed to add report', err);
    }
  };

  const getModalityIcon = (mod: string) => {
    switch (mod) {
      case 'voice_audio':
        return <Mic size={14} color="#38bdf8" />;
      case 'image_document':
        return <FileText size={14} color="#a855f7" />;
      default:
        return <Radio size={14} color="#10b981" />;
    }
  };

  const conflictClusters = activeIncident?.clusters.filter((c) => c.status === 'conflict') || [];
  const corroboratedClusters = activeIncident?.clusters.filter((c) => c.status === 'corroborated' || c.status === 'single_source') || [];
  const missingClusters = activeIncident?.clusters.filter((c) => c.status === 'missing') || [];

  return (
    <div>
      {/* 1. Header Sovereignty Strip */}
      <header className="top-strip" role="banner">
        <div className="brand-section">
          <div className="brand-logo">
            <Shield size={18} color="#38bdf8" />
            <span>RELAYZERO</span>
          </div>
          <span className="brand-badge">CH-DECISION-SUPPORT</span>
        </div>

        <div className="badges-group" role="region" aria-label="Sovereignty Status">
          <span className="status-chip chip-airgap">
            <Lock size={12} /> AIR-GAPPED (SOVEREIGN)
          </span>
          <span className="status-chip chip-egress">
            <CheckCircle size={12} /> EGRESS 0 VERIFIED
          </span>
          <span className="status-chip chip-model">
            APERTUS-1.5-8B
          </span>
        </div>

        <div className="header-controls">
          <label htmlFor="preset-select" className="sr-only">Demonstration Scenario</label>
          <select
            id="preset-select"
            className="preset-select"
            value={activeIncident?.preset_id || ''}
            onChange={(e) => handleSelectPreset(e.target.value)}
            disabled={loading}
          >
            <option value="alpine_tunnel_smoke">Preset: Alpine Tunnel Smoke (Gotthard)</option>
            <option value="flood_shelter_capacity">Preset: Rhône Flash Flood & Shelter</option>
            <option value="rail_power_failure">Preset: Rail Power Failure (Olten-Bern)</option>
          </select>

          <button
            className="btn-primary"
            onClick={handleProcessPipeline}
            disabled={loading || !activeIncident}
            aria-label="Process incident pipeline"
          >
            <RefreshCw size={13} className={loading ? 'spin' : ''} />
            {loading ? 'Processing Apertus...' : 'Compile Incident'}
          </button>
        </div>
      </header>

      {/* 2. Main Folio Layout */}
      <main className="folio-layout">
        {/* LEFT EVIDENCE RAIL */}
        <section className="folio-panel" aria-label="Submitted Evidence Rail">
          <div className="panel-header">
            <h2 className="panel-title">
              <Radio size={14} /> Evidence Rail ({activeIncident?.sources.length || 0})
            </h2>
            <button
              className="btn-secondary"
              style={{ padding: '3px 8px', fontSize: '11px' }}
              onClick={() => setShowAddModal(true)}
              aria-label="Ingest new report"
            >
              <PlusCircle size={12} /> Ingest
            </button>
          </div>

          <div className="panel-content">
            {activeIncident?.sources.map((src) => {
              const isSelected = selectedSourceId === src.report_id;
              return (
                <article
                  key={src.report_id}
                  className={`source-card ${isSelected ? 'active' : ''}`}
                  onClick={() => setSelectedSourceId(src.report_id)}
                  tabIndex={0}
                  role="button"
                  aria-pressed={isSelected}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') setSelectedSourceId(src.report_id);
                  }}
                >
                  <div className="source-header">
                    <span className="source-id-badge">{src.report_id}</span>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <span className="tag-badge" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        {getModalityIcon(src.modality)} {src.modality.replace('_', ' ')}
                      </span>
                      <span className="tag-badge">{src.language.toUpperCase()}</span>
                    </div>
                  </div>
                  <div className="source-meta">
                    <span><strong>Origin:</strong> {src.author_role}</span>
                    <span><strong>Channel:</strong> {src.source_channel}</span>
                    <span><strong>Received:</strong> {new Date(src.received_at).toLocaleTimeString()}</span>
                  </div>
                  <div className="source-text-preview">
                    {src.raw_content}
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        {/* CENTRAL EVIDENCE CANVAS */}
        <section className="folio-panel" aria-label="Evidence Reconciliation Canvas">
          <div className="panel-header">
            <h2 className="panel-title">
              <FileText size={14} /> Factual Claims Canvas ({activeIncident?.claims.length || 0})
            </h2>
            <div style={{ display: 'flex', gap: '6px' }}>
              {conflictClusters.length > 0 && (
                <span className="status-chip" style={{ background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24' }}>
                  {conflictClusters.length} Conflict(s)
                </span>
              )}
              {missingClusters.length > 0 && (
                <span className="status-chip" style={{ background: 'rgba(168, 85, 247, 0.2)', color: '#c084fc' }}>
                  {missingClusters.length} Missing
                </span>
              )}
            </div>
          </div>

          <div className="panel-content">
            {/* Active Incident Header */}
            <div style={{ padding: '10px 14px', background: 'var(--bg-surface)', borderRadius: '6px', border: '1px solid var(--border-dim)' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-dim)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>
                {activeIncident?.incident_id} • Status: {activeIncident?.status.toUpperCase()}
              </div>
              <h1 style={{ fontSize: '16px', fontWeight: 700, color: '#fff', marginTop: '2px' }}>
                {activeIncident?.title}
              </h1>
            </div>

            {/* If no claims processed yet */}
            {(!activeIncident?.claims || activeIncident.claims.length === 0) && (
              <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--text-dim)' }}>
                <Radio size={36} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
                <p style={{ fontSize: '13px' }}>No structured claims extracted yet.</p>
                <p style={{ fontSize: '12px' }}>Click <strong>"Compile Incident"</strong> to run Apertus isolated extraction & conflict reconciliation.</p>
              </div>
            )}

            {/* Contradictory Clusters First (High Priority) */}
            {conflictClusters.map((cluster) => (
              <div key={cluster.cluster_id} className="cluster-group conflict">
                <div className="cluster-header">
                  <span className="cluster-field-name">
                    ⚠️ {cluster.field.toUpperCase().replace('_', ' ')}
                  </span>
                  <span className="status-chip" style={{ background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24' }}>
                    CONTRADICTION
                  </span>
                </div>
                <div className="cluster-body">
                  <div className="conflict-banner">
                    <AlertTriangle size={15} style={{ flexShrink: 0, marginTop: '1px' }} />
                    <div>{cluster.conflict_explanation}</div>
                  </div>

                  <div className="claims-sublist">
                    {cluster.claims.map((claim) => (
                      <div
                        key={claim.claim_id}
                        className={`claim-row ${claim.operator_status === 'confirmed' ? 'confirmed' : ''}`}
                      >
                        <div className="claim-row-header">
                          <span className="claim-source-tag">{claim.source_id} ({claim.language.toUpperCase()})</span>
                          <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Confidence: {(claim.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div className="claim-value-text">{claim.operator_edited_value || claim.normalized_value}</div>
                        <div className="claim-evidence-quote">"{claim.evidence_pointer}"</div>
                        <div className="operator-actions-bar">
                          <button
                            className="action-btn-sm action-btn-confirm"
                            onClick={() => handleOperatorAction({ claim_id: claim.claim_id, action: 'confirm' })}
                          >
                            ✓ Confirm This Fact
                          </button>
                          <button
                            className="action-btn-sm"
                            onClick={() => {
                              const val = prompt('Edit factual value:', claim.normalized_value);
                              if (val) handleOperatorAction({ claim_id: claim.claim_id, action: 'edit', new_value: val });
                            }}
                          >
                            <Edit2 size={10} /> Edit
                          </button>
                          <button
                            className="action-btn-sm"
                            onClick={() => handleOperatorAction({ claim_id: claim.claim_id, action: 'reject' })}
                          >
                            <XCircle size={10} /> Reject
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}

            {/* Corroborated / Confirmed Clusters */}
            {corroboratedClusters.map((cluster) => (
              <div key={cluster.cluster_id} className="cluster-group corroborated">
                <div className="cluster-header">
                  <span className="cluster-field-name">
                    ✓ {cluster.field.toUpperCase().replace('_', ' ')}
                  </span>
                  <span className="status-chip chip-egress">
                    {cluster.claims.length > 1 ? `CORROBORATED (${cluster.claims.length}x)` : 'SINGLE SOURCE'}
                  </span>
                </div>
                <div className="cluster-body">
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '6px' }}>
                    {cluster.reconciled_value}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    Sources: {cluster.claims.map((c) => c.source_id).join(', ')}
                  </div>
                </div>
              </div>
            ))}

            {/* Missing Critical Fields */}
            {missingClusters.map((cluster) => (
              <div key={cluster.cluster_id} className="cluster-group missing">
                <div className="cluster-header">
                  <span className="cluster-field-name" style={{ color: '#c084fc' }}>
                    ❓ {cluster.field.toUpperCase().replace('_', ' ')}
                  </span>
                  <span className="status-chip" style={{ background: 'rgba(168, 85, 247, 0.2)', color: '#c084fc' }}>
                    MISSING FIELD
                  </span>
                </div>
                <div className="cluster-body">
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {cluster.conflict_explanation}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* RIGHT HUMAN DECISION PANEL */}
        <section className="folio-panel" aria-label="Human Operator Situation Brief">
          <div className="panel-header">
            <h2 className="panel-title">
              <Shield size={14} /> Situation Brief & Export
            </h2>
            <div style={{ display: 'flex', gap: '4px' }}>
              <button
                className="btn-secondary"
                style={{ padding: '3px 8px', fontSize: '11px' }}
                onClick={handleExportBundle}
                aria-label="Export sealed bundle"
              >
                <Download size={12} /> Bundle
              </button>
            </div>
          </div>

          <div className="panel-content">
            {activeIncident?.brief ? (
              <div className="brief-container">
                {/* Multilingual Tabs */}
                <div>
                  <div className="lang-tabs" role="tablist">
                    {(['en', 'de', 'fr', 'it'] as const).map((lang) => (
                      <button
                        key={lang}
                        className={`lang-tab-btn ${selectedLanguage === lang ? 'active' : ''}`}
                        onClick={() => setSelectedLanguage(lang)}
                        role="tab"
                        aria-selected={selectedLanguage === lang}
                      >
                        {lang.toUpperCase()}
                      </button>
                    ))}
                  </div>

                  <div className="brief-summary-box">
                    <p style={{ lineHeight: 1.6 }}>
                      {activeIncident.brief.multilingual_summaries[selectedLanguage] || activeIncident.brief.executive_summary}
                    </p>
                  </div>
                </div>

                {/* Operator Approval Status */}
                <div style={{
                  padding: '10px 12px',
                  borderRadius: '6px',
                  background: activeIncident.brief.approved_by_operator ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                  border: `1px solid ${activeIncident.brief.approved_by_operator ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}>
                  <div style={{ fontSize: '12px' }}>
                    <strong>Operator Status:</strong>{' '}
                    <span style={{ color: activeIncident.brief.approved_by_operator ? 'var(--status-confirmed)' : '#fbbf24' }}>
                      {activeIncident.brief.approved_by_operator ? 'APPROVED BY OPERATOR' : 'PENDING APPROVAL'}
                    </span>
                  </div>
                  {!activeIncident.brief.approved_by_operator ? (
                    <button className="btn-primary" style={{ padding: '4px 10px', fontSize: '11px' }} onClick={handleApproveBrief}>
                      Sign & Approve
                    </button>
                  ) : (
                    <span style={{ fontSize: '11px', color: 'var(--status-confirmed)' }}>✓ Signed</span>
                  )}
                </div>

                {/* Confirmed Facts Key-Value */}
                <div>
                  <h3 style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Confirmed Operational Facts
                  </h3>
                  <div className="brief-facts-list">
                    {Object.entries(activeIncident.brief.confirmed_facts).map(([k, v]) => (
                      <div key={k} className="fact-item">
                        <span className="fact-key">{k.toUpperCase().replace('_', ' ')}</span>
                        <span className="fact-val">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommended Operational Priorities */}
                {activeIncident.brief.recommended_priorities.length > 0 && (
                  <div>
                    <h3 style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                      Tactical Priorities
                    </h3>
                    <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '12px' }}>
                      {activeIncident.brief.recommended_priorities.map((pri, idx) => (
                        <li key={idx} style={{ padding: '6px 8px', background: 'var(--bg-base)', borderRadius: '4px', borderLeft: '2px solid #38bdf8' }}>
                          {pri}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Tamper-Evident Audit Trail */}
                <div style={{ marginTop: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <h3 style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Cryptographic Audit Chain
                    </h3>
                    <button
                      style={{ background: 'none', border: 'none', color: '#38bdf8', fontSize: '11px', cursor: 'pointer' }}
                      onClick={handleVerifyAudit}
                    >
                      Verify Chain
                    </button>
                  </div>
                  {auditStatus && (
                    <div style={{ fontSize: '11px', padding: '4px 8px', background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', borderRadius: '4px', marginBottom: '6px' }}>
                      {auditStatus}
                    </div>
                  )}
                  <div className="audit-list">
                    {activeIncident.audit_trail?.slice(-4).map((entry: any) => (
                      <div key={entry.entry_id} className="audit-entry-item">
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span className="audit-action-tag">{entry.action}</span>
                          <span style={{ color: 'var(--text-dim)' }}>{entry.actor}</span>
                        </div>
                        <div className="audit-hash-code">SHA256: {entry.hash_curr.slice(0, 24)}...</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--text-dim)' }}>
                <FileText size={36} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
                <p style={{ fontSize: '13px' }}>No situation brief compiled yet.</p>
                <p style={{ fontSize: '12px' }}>Compile incident to generate grounded multilingual summary.</p>
              </div>
            )}
          </div>
        </section>
      </main>

      {/* Add Report Modal */}
      {showAddModal && (
        <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <div className="modal-card">
            <div className="modal-header">
              <h2 id="modal-title" className="modal-title">Ingest Field Report</h2>
              <button
                style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}
                onClick={() => setShowAddModal(false)}
                aria-label="Close dialog"
              >
                ✕
              </button>
            </div>
            <form onSubmit={handleAddReportSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div className="form-group">
                <label className="form-label" htmlFor="report-modality">Modality</label>
                <select
                  id="report-modality"
                  className="form-select"
                  value={newReportModality}
                  onChange={(e: any) => setNewReportModality(e.target.value)}
                >
                  <option value="text">SMS / TETRA Text</option>
                  <option value="image_document">Scanned Protocol Form (OCR)</option>
                  <option value="voice_audio">Voice Radio / Audio Note (Transcript)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="report-lang">Language</label>
                <select
                  id="report-lang"
                  className="form-select"
                  value={newReportLang}
                  onChange={(e: any) => setNewReportLang(e.target.value)}
                >
                  <option value="de">German (Deutsch)</option>
                  <option value="fr">French (Français)</option>
                  <option value="it">Italian (Italiano)</option>
                  <option value="en">English</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="report-role">Sender Role</label>
                <input
                  id="report-role"
                  className="form-input"
                  value={newReportRole}
                  onChange={(e) => setNewReportRole(e.target.value)}
                  placeholder="e.g. Police Uri, Trapped Citizen, Civil Protection"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="report-content">Report Content</label>
                <textarea
                  id="report-content"
                  className="form-textarea"
                  value={newReportContent}
                  onChange={(e) => setNewReportContent(e.target.value)}
                  placeholder="Enter raw report, OCR extract, or voice transcript..."
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '8px' }}>
                <button type="button" className="btn-secondary" onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Ingest Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

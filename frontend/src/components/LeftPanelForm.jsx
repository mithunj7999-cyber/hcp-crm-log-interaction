import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  updateFormField, 
  resetForm, 
  saveInteraction, 
  fetchHcps, 
  fetchMaterials, 
  applySuggestion 
} from '../store/hcpSlice';
import { 
  User, 
  Calendar, 
  Clock, 
  Users, 
  MessageSquare, 
  Mic, 
  FileText, 
  Package, 
  Smile, 
  CheckSquare, 
  Plus, 
  ShieldAlert, 
  Loader2, 
  X,
  Search
} from 'lucide-react';

export default function LeftPanelForm() {
  const dispatch = useDispatch();
  const form = useSelector((state) => state.hcp.form);
  const hcps = useSelector((state) => state.hcp.hcps);
  const materialsList = useSelector((state) => state.hcp.materials);
  const suggestions = useSelector((state) => state.hcp.suggestions);
  const loadingSave = useSelector((state) => state.hcp.loadingSave);
  const loadingHcps = useSelector((state) => state.hcp.loadingHcps);
  const loadingMaterials = useSelector((state) => state.hcp.loadingMaterials);

  // Search dropdown open states
  const [hcpSearch, setHcpSearch] = useState('');
  const [showHcpDropdown, setShowHcpDropdown] = useState(false);
  const [materialSearch, setMaterialSearch] = useState('');
  const [showMaterialDropdown, setShowMaterialDropdown] = useState(false);

  // Voice Note states
  const [voiceConsent, setVoiceConsent] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingProgress, setRecordingProgress] = useState(0);
  const [voiceNoteActive, setVoiceNoteActive] = useState(false);

  const hcpRef = useRef(null);
  const materialRef = useRef(null);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (hcpRef.current && !hcpRef.current.contains(event.target)) {
        setShowHcpDropdown(false);
      }
      if (materialRef.current && !materialRef.current.contains(event.target)) {
        setShowMaterialDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Search HCPs on typing
  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (showHcpDropdown) {
        dispatch(fetchHcps(hcpSearch));
      }
    }, 300);
    return () => clearTimeout(delayDebounce);
  }, [hcpSearch, showHcpDropdown, dispatch]);

  // Search Materials on typing
  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (showMaterialDropdown) {
        dispatch(fetchMaterials(materialSearch));
      }
    }, 300);
    return () => clearTimeout(delayDebounce);
  }, [materialSearch, showMaterialDropdown, dispatch]);

  // Find current HCP name to show in the input box
  const selectedHcp = hcps.find(h => h.id === Number(form.hcp_id)) || null;
  const hcpInputDisplay = selectedHcp ? selectedHcp.name : hcpSearch;

  const handleFieldChange = (field, value) => {
    dispatch(updateFormField({ field, value }));
  };

  const handleSelectHcp = (hcp) => {
    handleFieldChange('hcp_id', hcp.id);
    setHcpSearch(hcp.name);
    setShowHcpDropdown(false);
  };

  const handleAddMaterial = (materialName) => {
    const current = form.materials_shared ? form.materials_shared.split(',').map(s => s.trim()) : [];
    if (!current.includes(materialName)) {
      const updated = [...current, materialName].filter(Boolean).join(', ');
      handleFieldChange('materials_shared', updated);
    }
    setMaterialSearch('');
    setShowMaterialDropdown(false);
  };

  const handleAddSample = () => {
    const sampleName = prompt("Enter Sample Name to distribute (e.g. 'OncoBoost 50mg Sample'):");
    if (sampleName) {
      const current = form.samples_distributed ? form.samples_distributed.split(',').map(s => s.trim()) : [];
      if (!current.includes(sampleName)) {
        const updated = [...current, sampleName].filter(Boolean).join(', ');
        handleFieldChange('samples_distributed', updated);
      }
    }
  };

  // Simulate Mic voice note logic
  const handleMicClick = () => {
    if (!voiceConsent) {
      setVoiceNoteActive(true);
      return;
    }
    startSimulatedRecording();
  };

  const startSimulatedRecording = () => {
    setIsRecording(true);
    setRecordingProgress(0);
    const interval = setInterval(() => {
      setRecordingProgress(p => {
        if (p >= 100) {
          clearInterval(interval);
          setIsRecording(false);
          // Transcribe a simulated text to the topics discussed box
          const transcripts = [
            "Discussed clinical efficacy results of OncoBoost in lung cancer patients, with high interest in prescribing guidelines.",
            "Discussed patient enrollment for the upcoming heart failure outcomes trial and CardioShield dosing scheduling.",
            "Talked about insulin pen injection technique and patient compliance using the GlucoBalance guide."
          ];
          const randomTranscript = transcripts[Math.floor(Math.random() * transcripts.length)];
          handleFieldChange('topics_discussed', randomTranscript);
          return 0;
        }
        return p + 10;
      });
    }, 300);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.hcp_id) {
      alert("Please select a Healthcare Professional.");
      return;
    }
    dispatch(saveInteraction(form));
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <FileText size={20} />
        <h2>Structured Interaction Log</h2>
      </div>

      <div className="panel-content">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            
            {/* HCP Name - Searchable Select */}
            <div className="form-group full-width" ref={hcpRef}>
              <label>HCP Name</label>
              <div className="search-wrapper">
                <input
                  type="text"
                  placeholder="Type to search HCP..."
                  value={hcpInputDisplay}
                  onChange={(e) => {
                    setHcpSearch(e.target.value);
                    if (form.hcp_id) handleFieldChange('hcp_id', '');
                    setShowHcpDropdown(true);
                  }}
                  onFocus={() => setShowHcpDropdown(true)}
                />
                {showHcpDropdown && (
                  <div className="search-results-dropdown">
                    {loadingHcps && <div className="search-result-item">Searching...</div>}
                    {!loadingHcps && hcps.length === 0 && (
                      <div className="search-result-item">No HCPs found</div>
                    )}
                    {hcps.map((h) => (
                      <div 
                        key={h.id} 
                        className="search-result-item" 
                        onClick={() => handleSelectHcp(h)}
                      >
                        {h.name} ({h.specialty} - {h.institution})
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Interaction Type */}
            <div className="form-group">
              <label>Interaction Type</label>
              <select
                value={form.interaction_type}
                onChange={(e) => handleFieldChange('interaction_type', e.target.value)}
              >
                <option value="Meeting">Meeting</option>
                <option value="Call">Call</option>
                <option value="Email">Email</option>
                <option value="Video Call">Video Call</option>
                <option value="Conference">Conference</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {/* Date + Time */}
            <div className="form-group">
              <label>Date</label>
              <input
                type="date"
                value={form.date}
                onChange={(e) => handleFieldChange('date', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Time</label>
              <input
                type="time"
                value={form.time || ''}
                onChange={(e) => handleFieldChange('time', e.target.value)}
              />
            </div>

            {/* Attendees */}
            <div className="form-group">
              <label>Attendees</label>
              <input
                type="text"
                placeholder="Dr. Smith, John (Rep)"
                value={form.attendees || ''}
                onChange={(e) => handleFieldChange('attendees', e.target.value)}
              />
            </div>

            {/* Topics Discussed */}
            <div className="form-group full-width">
              <label>Topics Discussed</label>
              <div className="textarea-wrapper">
                <textarea
                  rows="3"
                  placeholder="What was discussed during the meeting?"
                  value={form.topics_discussed || ''}
                  onChange={(e) => handleFieldChange('topics_discussed', e.target.value)}
                />
                <button
                  type="button"
                  className={`mic-button ${isRecording ? 'recording' : ''}`}
                  onClick={handleMicClick}
                  title="Simulate Voice Dictation"
                >
                  <Mic size={18} />
                </button>
              </div>

              {/* Consent requirement banner/modal details */}
              {voiceNoteActive && !voiceConsent && (
                <div className="consent-banner">
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <ShieldAlert size={16} style={{ color: 'var(--accent-primary)' }} />
                    <p style={{ fontWeight: '600' }}>Patient/HCP Consent Required</p>
                  </div>
                  <p>Logging voice note requires verbal consent from the participant. Do you confirm consent has been acquired?</p>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      type="button"
                      className="consent-btn"
                      onClick={() => {
                        setVoiceConsent(true);
                        setVoiceNoteActive(false);
                        startSimulatedRecording();
                      }}
                    >
                      Yes, Consent Acquired
                    </button>
                    <button
                      type="button"
                      className="consent-btn"
                      style={{ background: 'transparent', color: 'var(--text-secondary)' }}
                      onClick={() => setVoiceNoteActive(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {isRecording && (
                <div style={{ fontSize: '0.75rem', color: 'var(--accent-secondary)', marginTop: '0.25rem' }}>
                  Simulating voice transcribing: {recordingProgress}%
                </div>
              )}
            </div>

            {/* Materials Shared */}
            <div className="form-group" ref={materialRef}>
              <label>Materials Shared</label>
              <div className="search-wrapper">
                <input
                  type="text"
                  placeholder="Search and add materials..."
                  value={materialSearch}
                  onChange={(e) => {
                    setMaterialSearch(e.target.value);
                    setShowMaterialDropdown(true);
                  }}
                  onFocus={() => setShowMaterialDropdown(true)}
                />
                {showMaterialDropdown && (
                  <div className="search-results-dropdown">
                    {loadingMaterials && <div className="search-result-item">Searching...</div>}
                    {!loadingMaterials && materialsList.length === 0 && (
                      <div className="search-result-item">No materials found</div>
                    )}
                    {materialsList.map((m) => (
                      <div 
                        key={m.id} 
                        className="search-result-item" 
                        onClick={() => handleAddMaterial(m.name)}
                      >
                        {m.name} ({m.type})
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <input
                type="text"
                disabled
                placeholder="Added materials will appear here"
                value={form.materials_shared || ''}
                style={{ marginTop: '0.5rem', opacity: 0.8 }}
              />
            </div>

            {/* Samples Distributed */}
            <div className="form-group">
              <label>Samples Distributed</label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="text"
                  disabled
                  placeholder="No samples added"
                  value={form.samples_distributed || ''}
                />
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleAddSample}
                  style={{ padding: '0.5rem 1rem' }}
                >
                  <Plus size={16} />
                </button>
              </div>
            </div>

            {/* HCP Sentiment */}
            <div className="form-group full-width">
              <label>Observed HCP Sentiment</label>
              <div className="sentiment-group">
                {['Positive', 'Neutral', 'Negative'].map((s) => (
                  <label key={s} className="sentiment-radio">
                    <input
                      type="radio"
                      name="sentiment"
                      value={s}
                      checked={form.sentiment === s}
                      onChange={(e) => handleFieldChange('sentiment', e.target.value)}
                    />
                    <div className={`sentiment-card ${s.toLowerCase()}`}>
                      <Smile size={16} />
                      {s}
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Outcomes */}
            <div className="form-group full-width">
              <label>Outcomes</label>
              <textarea
                rows="2"
                placeholder="Interaction outcomes..."
                value={form.outcomes || ''}
                onChange={(e) => handleFieldChange('outcomes', e.target.value)}
              />
            </div>

            {/* Follow-up Actions */}
            <div className="form-group full-width">
              <label>Follow-up Actions</label>
              <textarea
                rows="2"
                placeholder="Next steps or follow-ups..."
                value={form.follow_up_actions || ''}
                onChange={(e) => handleFieldChange('follow_up_actions', e.target.value)}
              />
            </div>

            {/* AI Suggested Follow-ups */}
            <div className="form-group full-width">
              <label>AI Suggested Follow-ups</label>
              <div className="chips-container">
                {suggestions.map((s, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="chip"
                    onClick={() => dispatch(applySuggestion(s))}
                  >
                    <CheckSquare size={12} style={{ color: 'var(--accent-primary)' }} />
                    {s}
                  </button>
                ))}
              </div>
            </div>

          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={() => dispatch(resetForm())}
            >
              Reset
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loadingSave}
            >
              {loadingSave ? <Loader2 size={16} className="animate-spin" /> : 'Log Interaction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

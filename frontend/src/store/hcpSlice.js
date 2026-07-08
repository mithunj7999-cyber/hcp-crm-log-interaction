import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// ── Thunks ─────────────────────────────────────────────────────────────

// Send chat message to LangGraph agent
export const sendChatMessage = createAsyncThunk(
  'hcp/sendChatMessage',
  async ({ message, history }, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, history }),
      });
      if (!response.ok) {
        throw new Error('Failed to communicate with the AI assistant.');
      }
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Fetch HCP search list
export const fetchHcps = createAsyncThunk(
  'hcp/fetchHcps',
  async (search, { rejectWithValue }) => {
    try {
      const queryParam = search ? `?search=${encodeURIComponent(search)}` : '';
      const response = await fetch(`/api/hcps/${queryParam}`);
      if (!response.ok) throw new Error('Failed to fetch HCP list.');
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Fetch materials search list
export const fetchMaterials = createAsyncThunk(
  'hcp/fetchMaterials',
  async (search, { rejectWithValue }) => {
    try {
      const queryParam = search ? `?search=${encodeURIComponent(search)}` : '';
      const response = await fetch(`/api/materials/${queryParam}`);
      if (!response.ok) throw new Error('Failed to fetch materials list.');
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Submit structured form interaction to DB
export const saveInteraction = createAsyncThunk(
  'hcp/saveInteraction',
  async (interactionData, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/interactions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(interactionData),
      });
      if (!response.ok) throw new Error('Failed to log interaction to DB.');
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// ── Initial State ──────────────────────────────────────────────────────

const initialFormState = {
  hcp_id: '',
  interaction_type: 'Meeting',
  date: new Date().toISOString().split('T')[0],
  time: '',
  attendees: '',
  topics_discussed: '',
  materials_shared: '',
  samples_distributed: '',
  sentiment: 'Neutral',
  outcomes: '',
  follow_up_actions: '',
};

const initialState = {
  form: { ...initialFormState },
  chatMessages: [
    {
      role: 'assistant',
      content: 'Hello! I can help you log your interaction. Just describe the conversation naturally (e.g., "Met Dr. Sarah Chen, discussed OncoBoost efficacy and left a sample..."), and I\'ll populate the form for you.'
    }
  ],
  suggestions: [
    'Schedule follow-up meeting in 2 weeks',
    'Send OncoBoost Efficacy Brochure PDF',
    'Follow up next week'
  ],
  hcps: [],
  materials: [],
  loadingChat: false,
  loadingSave: false,
  loadingHcps: false,
  loadingMaterials: false,
  error: null,
};

// ── Slice ──────────────────────────────────────────────────────────────

const hcpSlice = createSlice({
  name: 'hcp',
  initialState,
  reducers: {
    updateFormField: (state, action) => {
      const { field, value } = action.payload;
      state.form[field] = value;
    },
    resetForm: (state) => {
      state.form = { ...initialFormState };
    },
    addChatMessage: (state, action) => {
      state.chatMessages.push(action.payload);
    },
    applySuggestion: (state, action) => {
      const text = action.payload;
      if (state.form.follow_up_actions) {
        state.form.follow_up_actions += `, ${text}`;
      } else {
        state.form.follow_up_actions = text;
      }
    },
    setSuggestions: (state, action) => {
      state.suggestions = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      // sendChatMessage
      .addCase(sendChatMessage.pending, (state) => {
        state.loadingChat = true;
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.loadingChat = false;
        const { reply, extracted_data, suggestions } = action.payload;
        
        state.chatMessages.push({ role: 'assistant', content: reply });
        
        // Auto-populate structured form fields from parsed AI response
        if (extracted_data) {
          Object.keys(extracted_data).forEach((key) => {
            if (extracted_data[key] !== null && extracted_data[key] !== undefined && key in state.form) {
              state.form[key] = extracted_data[key];
            }
          });
        }
        
        // Set new AI Suggested Follow-ups
        if (suggestions && suggestions.length > 0) {
          state.suggestions = suggestions;
        }
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.loadingChat = false;
        state.error = action.payload;
        state.chatMessages.push({
          role: 'assistant',
          content: 'Sorry, I encountered an error communicating with the agent server. Please verify your Groq API key config.'
        });
      })
      
      // fetchHcps
      .addCase(fetchHcps.pending, (state) => {
        state.loadingHcps = true;
      })
      .addCase(fetchHcps.fulfilled, (state, action) => {
        state.loadingHcps = false;
        state.hcps = action.payload;
      })
      .addCase(fetchHcps.rejected, (state) => {
        state.loadingHcps = false;
      })

      // fetchMaterials
      .addCase(fetchMaterials.pending, (state) => {
        state.loadingMaterials = true;
      })
      .addCase(fetchMaterials.fulfilled, (state, action) => {
        state.loadingMaterials = false;
        state.materials = action.payload;
      })
      .addCase(fetchMaterials.rejected, (state) => {
        state.loadingMaterials = false;
      })

      // saveInteraction
      .addCase(saveInteraction.pending, (state) => {
        state.loadingSave = true;
        state.error = null;
      })
      .addCase(saveInteraction.fulfilled, (state) => {
        state.loadingSave = false;
        state.form = { ...initialFormState }; // Reset form on success
        state.chatMessages.push({
          role: 'assistant',
          content: 'Great! The interaction has been successfully logged to the database. Feel free to log another interaction or ask me questions.'
        });
      })
      .addCase(saveInteraction.rejected, (state, action) => {
        state.loadingSave = false;
        state.error = action.payload;
      });
  },
});

export const { updateFormField, resetForm, addChatMessage, applySuggestion, setSuggestions } = hcpSlice.actions;
export default hcpSlice.reducer;

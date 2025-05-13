import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ChatState {
  pendingMessage: string | null;
}

const initialState: ChatState = {
  pendingMessage: null
};

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setPendingMessage: (state, action: PayloadAction<string>) => {
      state.pendingMessage = action.payload;
    },
    clearPendingMessage: (state) => {
      state.pendingMessage = null;
    }
  }
});

export const { setPendingMessage, clearPendingMessage } = chatSlice.actions;
export default chatSlice.reducer; 
import { clearPendingMessage, setPendingMessage } from '@/redux/chatSlice';
import { RootState } from '@/redux/store';
import { useDispatch, useSelector } from 'react-redux';

export const useChat = () => {
  const dispatch = useDispatch();
  const pendingMessage = useSelector((state: RootState) => state.chat.pendingMessage);
  
  const setPending = (message: string) => {
    dispatch(setPendingMessage(message));
  };
  
  const clearPending = () => {
    dispatch(clearPendingMessage());
  };
  
  return {
    pendingMessage,
    setPending,
    clearPending
  };
}; 
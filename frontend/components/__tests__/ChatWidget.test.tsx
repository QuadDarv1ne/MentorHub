/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChatWidget } from '../ChatWidget';

const mockConnect = jest.fn();
const mockDisconnect = jest.fn();
const mockWsSend = jest.fn();
let mockConnectionStatus = 'connected';

const mockUseWebSocket = jest.fn(() => ({
  connectionStatus: mockConnectionStatus,
  sendMessage: mockWsSend,
  connect: mockConnect,
  disconnect: mockDisconnect,
}));

jest.mock('@/hooks/useWebSocket', () => ({
  useWebSocket: (...args: any[]) => mockUseWebSocket(...args),
}));

jest.mock('lucide-react', () => ({
  Send: () => <svg data-testid="send-icon" />,
  X: () => <svg data-testid="x-icon" />,
  MessageCircle: () => <svg data-testid="message-circle-icon" />,
  User: () => <svg data-testid="user-icon" />,
  Check: () => <svg data-testid="check-icon" />,
  CheckCheck: () => <svg data-testid="check-check-icon" />,
}));

type MessageHandler = (data: Record<string, unknown>) => void;

beforeAll(() => {
  Element.prototype.scrollIntoView = jest.fn();
});

describe('ChatWidget', () => {
  const defaultProps = {
    recipientId: 42,
    recipientName: 'John Doe',
    isOpen: true,
    onClose: jest.fn(),
  };

  let onMessageHandler: MessageHandler;

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    localStorage.setItem('user_id', '1');
    mockConnectionStatus = 'connected';
    mockUseWebSocket.mockImplementation((opts: { onMessage: MessageHandler }) => {
      onMessageHandler = opts.onMessage;
      return {
        connectionStatus: mockConnectionStatus,
        sendMessage: mockWsSend,
        connect: mockConnect,
        disconnect: mockDisconnect,
      };
    });
  });

  it('renders null when isOpen is false', () => {
    const { container } = render(<ChatWidget {...defaultProps} isOpen={false} />);
    expect(container.innerHTML).toBe('');
  });

  it('renders chat header with recipient name', () => {
    render(<ChatWidget {...defaultProps} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('shows online status when connected', () => {
    render(<ChatWidget {...defaultProps} />);
    expect(screen.getByText('Online')).toBeInTheDocument();
  });

  it('connects WebSocket when opened', () => {
    render(<ChatWidget {...defaultProps} />);
    expect(mockConnect).toHaveBeenCalled();
  });

  it('disconnects WebSocket on close', () => {
    const { rerender } = render(<ChatWidget {...defaultProps} />);
    rerender(<ChatWidget {...defaultProps} isOpen={false} />);
    expect(mockDisconnect).toHaveBeenCalled();
  });

  it('renders input and send button', () => {
    render(<ChatWidget {...defaultProps} />);
    expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
    expect(screen.getByLabelText('Send message')).toBeInTheDocument();
  });

  it('shows empty state when no messages', () => {
    render(<ChatWidget {...defaultProps} />);
    expect(screen.getByText('Start the conversation')).toBeInTheDocument();
  });

  it('calls onClose when close button clicked', () => {
    const onClose = jest.fn();
    render(<ChatWidget {...defaultProps} onClose={onClose} />);
    fireEvent.click(screen.getByLabelText('Close chat'));
    expect(onClose).toHaveBeenCalled();
  });

  it('disables send button when input is empty', () => {
    render(<ChatWidget {...defaultProps} />);
    expect(screen.getByLabelText('Send message')).toBeDisabled();
  });

  it('enables send button when input has text', () => {
    render(<ChatWidget {...defaultProps} />);
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'Hello' } });
    expect(screen.getByLabelText('Send message')).not.toBeDisabled();
  });

  it('sends message on button click', () => {
    render(<ChatWidget {...defaultProps} />);
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(screen.getByLabelText('Send message'));
    expect(mockWsSend).toHaveBeenCalledWith({
      type: 'message',
      recipient_id: 42,
      content: 'Hello',
    });
  });

  it('clears input after sending message', () => {
    render(<ChatWidget {...defaultProps} />);
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(screen.getByLabelText('Send message'));
    expect(input).toHaveValue('');
  });

  it('sends message on Enter key press', () => {
    render(<ChatWidget {...defaultProps} />);
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });
    expect(mockWsSend).toHaveBeenCalledWith({
      type: 'message',
      recipient_id: 42,
      content: 'Hello',
    });
  });

  it('does not send message on Shift+Enter', () => {
    render(<ChatWidget {...defaultProps} />);
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'Hello' } });
    jest.clearAllMocks();
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true });
    expect(mockWsSend).not.toHaveBeenCalledWith(expect.objectContaining({ type: 'message' }));
  });

  it('renders received messages', () => {
    render(<ChatWidget {...defaultProps} />);
    act(() => {
      onMessageHandler({
        type: 'message',
        id: 1,
        sender_id: 42,
        sender_username: 'johndoe',
        recipient_id: 1,
        content: 'Hi there!',
        timestamp: new Date().toISOString(),
      });
    });
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });

  it('renders sent messages', () => {
    render(<ChatWidget {...defaultProps} />);
    act(() => {
      onMessageHandler({
        type: 'message',
        id: 1,
        sender_id: 1,
        sender_username: 'me',
        recipient_id: 42,
        content: 'My message',
        timestamp: new Date().toISOString(),
      });
    });
    expect(screen.getByText('My message')).toBeInTheDocument();
  });

  it('shows typing indicator', () => {
    render(<ChatWidget {...defaultProps} />);
    act(() => {
      onMessageHandler({ type: 'typing' });
    });
    const typingDots = document.querySelectorAll('.animate-bounce');
    expect(typingDots.length).toBe(3);
  });

  it('updates message read status on read event', () => {
    render(<ChatWidget {...defaultProps} />);
    act(() => {
      onMessageHandler({
        type: 'message',
        id: 1,
        sender_id: 1,
        sender_username: 'me',
        recipient_id: 42,
        content: 'Check read',
        timestamp: new Date().toISOString(),
        is_read: false,
      });
      onMessageHandler({ type: 'read', message_id: 1 });
    });
    const checkIcons = screen.getAllByTestId('check-check-icon');
    expect(checkIcons.length).toBeGreaterThan(0);
  });

  it('sends typing indicator on input change', () => {
    render(<ChatWidget {...defaultProps} />);
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'T' } });
    expect(mockWsSend).toHaveBeenCalledWith({
      type: 'typing',
      recipient_id: 42,
    });
  });

  it('disables input when disconnected', () => {
    mockConnectionStatus = 'disconnected';
    render(<ChatWidget {...defaultProps} />);
    expect(screen.getByPlaceholderText('Type a message...')).toBeDisabled();
  });

  it('renders close button', () => {
    render(<ChatWidget {...defaultProps} />);
    expect(screen.getByLabelText('Close chat')).toBeInTheDocument();
  });

  it('loads current user id from localStorage', () => {
    localStorage.setItem('user_id', '5');
    render(<ChatWidget {...defaultProps} />);
    act(() => {
      onMessageHandler({
        type: 'message',
        id: 1,
        sender_id: 5,
        sender_username: 'me',
        recipient_id: 42,
        content: 'Sent by me',
        timestamp: new Date().toISOString(),
      });
    });
    expect(screen.getByText('Sent by me')).toBeInTheDocument();
  });
});

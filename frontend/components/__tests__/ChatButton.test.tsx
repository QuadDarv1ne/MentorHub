/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChatButton } from '../ChatButton';

jest.mock('../ChatWidget', () => ({
  ChatWidget: ({ isOpen, onClose: _onClose, recipientName }: { isOpen: boolean; onClose: () => void; recipientName: string }) =>
    isOpen ? <div data-testid="chat-widget">Chat with {recipientName}</div> : null,
}));

describe('ChatButton', () => {
  const defaultProps = {
    recipientId: 42,
    recipientName: 'John Doe',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders chat button with correct aria-label', () => {
    render(<ChatButton {...defaultProps} />);
    expect(screen.getByLabelText('Chat with John Doe')).toBeInTheDocument();
  });

  it('shows online indicator', () => {
    render(<ChatButton {...defaultProps} />);
    expect(screen.getByText('Online now')).toBeInTheDocument();
  });

  it('opens ChatWidget on button click', () => {
    render(<ChatButton {...defaultProps} />);
    expect(screen.queryByTestId('chat-widget')).not.toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('Chat with John Doe'));
    expect(screen.getByTestId('chat-widget')).toBeInTheDocument();
    expect(screen.getByText('Chat with John Doe')).toBeInTheDocument();
  });

  it('closes ChatWidget when onClose is triggered', () => {
    render(<ChatButton {...defaultProps} />);
    fireEvent.click(screen.getByLabelText('Chat with John Doe'));
    expect(screen.getByTestId('chat-widget')).toBeInTheDocument();
  });

  it('renders different recipient name', () => {
    render(<ChatButton recipientId={7} recipientName="Jane Smith" />);
    expect(screen.getByLabelText('Chat with Jane Smith')).toBeInTheDocument();
  });

  it('renders the MessageCircle icon', () => {
    render(<ChatButton {...defaultProps} />);
    const button = screen.getByLabelText('Chat with John Doe');
    expect(button.querySelector('svg')).toBeInTheDocument();
  });

  it('has sr-only span for accessibility', () => {
    render(<ChatButton {...defaultProps} />);
    const srSpan = screen.getByText('Open chat with John Doe');
    expect(srSpan).toHaveClass('sr-only');
  });
});


export type MessageSender = 'user' | 'ai';

export interface Message {
  id: string;
  text: string;
  sender: MessageSender;
}

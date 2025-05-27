import React, { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { tutorApi } from '@/services/api';
import { Atom } from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import TutorSelect from './TutorSelect';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { Input } from "@/components/ui/input";

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  type?: 'search' | 'ai' | 'dialogue' | 'info' | 'error' | 'status' | 'grammar' | 'vocabulary' | 'culture' | 'explanation' | 'problems' | 'visuals' | 'pronunciation';
  data?: any;
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([{
    id: uuidv4(),
    content: "Welcome to Poly Tutor! Select a subject and I'll help you learn.",
    sender: 'bot',
    type: 'info',
    data: { type: 'info', content: "Welcome message" }
  }]);

  const [streaming, setStreaming] = useState(false);
  const [subject, setSubject] = useState<'physics' | 'chemistry' | 'language' | null>(null);
  const [languageCode, setLanguageCode] = useState<string>('en');
  const [showDialoguePrompt, setShowDialoguePrompt] = useState(false);
  const [dialogueTopicInput, setDialogueTopicInput] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const currentStreamReceivedPartsRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const resetMessages = () => {
    setMessages([{
      id: uuidv4(),
      content: "Welcome to Poly Tutor! Select a subject and I'll help you learn.",
      sender: 'bot',
      type: 'info',
      data: { type: 'info', content: "Welcome message" }
    }]);
    currentStreamReceivedPartsRef.current.clear();
    setDialogueTopicInput("");
  };

  const handleSubjectChange = (newSubject: 'physics' | 'chemistry' | 'language') => {
    setSubject(newSubject);
    resetMessages();
  };

  const handleLanguageChange = (newCode: string) => {
    setLanguageCode(newCode);
    resetMessages();
  };

  const handleExplain = async (query: string) => {
    if (!query.trim()) return;
    if (!subject) {
      setMessages(prev => [
        ...prev,
        {
          id: uuidv4(),
          content: query,
          sender: 'user',
          type: 'ai',
        },
        {
          id: uuidv4(),
          content: "Please select a subject before asking questions.",
          sender: 'bot',
          type: 'info',
          data: { type: 'info', content: "Prompt to select subject" },
        },
      ]);
      return;
    }

    const userMessage: Message = {
      id: uuidv4(),
      content: query,
      sender: 'user',
      type: 'ai',
    };
    setMessages(prev => [...prev, userMessage]);

    setStreaming(true);
    currentStreamReceivedPartsRef.current.clear();
    abortControllerRef.current = new AbortController();

    let streamEndedSuccessfully = false;
    let receivedErrorInStream = false;

    try {
      await tutorApi.streamExplain(subject, query, (data) => {
        const messageType = data.type as Message['type'];
        const contentToAdd = data.content;

        if (contentToAdd && contentToAdd.trim() !== "") {
          setMessages((prev) => [...prev, {
            id: uuidv4(),
            content: contentToAdd,
            sender: 'bot',
            type: messageType || 'ai',
            data: data,
          }]);

          if (messageType === 'error') receivedErrorInStream = true;
          else if (messageType !== 'info' && messageType !== 'status') currentStreamReceivedPartsRef.current.add(messageType);
        }
      }, languageCode);

      if (!receivedErrorInStream) streamEndedSuccessfully = true;
    } catch (err: any) {
      streamEndedSuccessfully = false;
      let errorContent = 'Failed to get explanation. Please try again.';
      let errorType: Message['type'] = 'error';

      if (err.name === 'AbortError') {
        if (!receivedErrorInStream) {
          errorContent = "Request cancelled.";
          errorType = 'info';
        } else {
          errorContent = "";
        }
      }

      if (errorContent) {
        setMessages(prev => [...prev, {
          id: uuidv4(),
          content: errorContent,
          sender: 'bot',
          type: errorType,
          data: { error: err, type: errorType, content: errorContent },
        }]);
      }
    } finally {
      setStreaming(false);
      abortControllerRef.current = null;

      if (subject === 'language' && streamEndedSuccessfully) setShowDialoguePrompt(true);
    }
  };

  const handleConfirmDialogue = async () => {
    const topic = dialogueTopicInput.trim();
    if (!topic) return;
    setShowDialoguePrompt(false);

    try {
      const response = await tutorApi.createDialogue(topic, languageCode);
      setMessages(prev => [...prev, {
        id: uuidv4(),
        content: response.content,
        sender: 'bot',
        type: response.type || 'dialogue',
        data: response,
      }]);
    } catch (error: any) {
      const errorContent = `Failed to create dialogue for "${topic}": ${error.message}`;
      setMessages(prev => [...prev, {
        id: uuidv4(),
        content: errorContent,
        sender: 'bot',
        type: 'error',
        data: { type: 'error', content: errorContent, error: error },
      }]);
    } finally {
      setDialogueTopicInput("");
    }
  };

  const handleCancelDialogue = () => {
    setShowDialoguePrompt(false);
    setDialogueTopicInput("");
    setMessages(prev => [...prev, {
      id: uuidv4(),
      content: "Okay, let me know if you want to practice later!",
      sender: 'bot',
      type: 'info',
      data: { type: 'info', content: "Okay, let me know if you want to practice later!" },
    }]);
  };

  const handleInputSubmit = async (message: string, type: "search" | "ai") => {
    if (!subject) {
      setMessages(prev => [
        ...prev,
        {
          id: uuidv4(),
          content: message,
          sender: 'user',
          type: type,
        },
        {
          id: uuidv4(),
          content: "Please select a subject before continuing.",
          sender: 'bot',
          type: 'info',
          data: { type: 'info', content: "Prompt to select subject" },
        },
      ]);
      return;
    }

    if (type === 'ai') {
      handleExplain(message);
    } else if (type === 'search') {
      try {
        const userMessage: Message = {
          id: uuidv4(),
          content: message,
          sender: 'user',
          type: 'search',
        };
        setMessages(prev => [...prev, userMessage]);

        const response = await tutorApi.search(subject, message, languageCode);
        setMessages(prev => [
          ...prev,
          ...response.results.map((result) => ({
            id: uuidv4(),
            content: result.content,
            sender: 'bot',
            type: 'search',
            data: result,
          })),
        ]);
      } catch (error: any) {
        const errorContent = `Failed to search for "${message}": ${error.message}`;
        setMessages(prev => [...prev, {
          id: uuidv4(),
          content: errorContent,
          sender: 'bot',
          type: 'error',
          data: { type: 'error', content: errorContent, error: error },
        }]);
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="p-4 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center mb-4">
          <Atom className="w-10 h-10 text-gray-800 dark:text-gray-100 mr-3" />
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100 font-sans">Poly Tutor</h1>
        </div>
        <TutorSelect
          onSubjectChange={handleSubjectChange}
          onLanguageChange={handleLanguageChange}
          showLanguageSelect={subject === 'language'}
        />
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message.content}
            isBot={message.sender === 'bot'}
            type={message.type || 'ai'}
            data={message.data}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSubmit={handleInputSubmit} />

      <AlertDialog
        open={showDialoguePrompt}
        onOpenChange={(open: boolean) => {
          setShowDialoguePrompt(open);
          if (!open) {
            setDialogueTopicInput('');
          }
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Practice Conversation?</AlertDialogTitle>
            <AlertDialogDescription>
              Please enter a topic you'd like to practice a conversation about.
            </AlertDialogDescription>
          </AlertDialogHeader>

          <div className="py-2">
            <Input
              placeholder="Enter conversation topic..."
              value={dialogueTopicInput}
              onChange={(e) => setDialogueTopicInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && dialogueTopicInput.trim()) {
                  handleConfirmDialogue();
                }
              }}
            />
          </div>

          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleCancelDialogue}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDialogue}
              disabled={!dialogueTopicInput.trim()}
            >
              Start Practice
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

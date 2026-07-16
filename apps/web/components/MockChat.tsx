"use client";

import { SelectionLookupText } from "@/components/SelectionLookupText";
import type { Term } from "@/lib/api";

export type ChatMessage = {
  id: string;
  author: string;
  time: string;
  text: string;
};

type Props = {
  messages: ChatMessage[];
  terms: Term[];
  enabled: boolean;
};

export function MockChat({ messages, terms, enabled }: Props) {
  return (
    <div className="mock-chat">

      <div className="mock-chat-header">

        <div className="mock-chat-channel">
          <img
            src="/microsoft-team-logo.png"
            alt="Microsoft Teams"
            className="teams-logo"
          />

          <span className="mock-chat-title">
            # platform-engineering
          </span>
        </div>

        <span className="mock-chat-hint">
          {enabled
            ? "Double-click or highlight a word for its definition"
            : "Turn jargon assist on to look up words"}
        </span>

      </div>

      <div className="mock-chat-thread">
        {messages.map((msg) => (
          <div key={msg.id} className="mock-chat-message">
            <div className="mock-chat-meta">
              <strong>{msg.author}</strong>
              <span>{msg.time}</span>
            </div>

            <div className="mock-chat-bubble">
              <SelectionLookupText
                text={msg.text}
                terms={terms}
                enabled={enabled}
              />
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}

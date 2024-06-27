"use client";
import { useState, useEffect, useRef } from "react";
import { getUserAvatar, getUsernameColor } from "@/lib/utils";
import { Badge } from "./ui/badge";
import Image from "next/image";
import { useUser } from "@/context/user.context";

import useSWR from "swr";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Input } from "./ui/input";
import useKeypress from "@/hooks/use-key-press";

type Message = {
  message: string;
  username: string;
};

const fetcher = (url: string) =>
  fetch(url, {
    method: "GET",
  }).then((res) => res.json());

export function Chat({
  username,
  stream_id,
  isStreaming,
}: {
  username: string;
  stream_id: string;
  isStreaming: boolean;
}) {
  const formatViewers = (viewers: number) => {
    return viewers.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  const [viewers, setViewers] = useState(0);
  const { user } = useUser();

  const [messageHistory, setMessageHistory] = useState<Message[]>([]);
  const messageRef = useRef<HTMLInputElement>(null);

  const { data, error, isLoading } = useSWR("/api/refresh-token/", fetcher);

  const { sendMessage, readyState, lastMessage } = useWebSocket(
    `ws://127.0.0.1:8000/comment/${stream_id}${data?.data?.access ? `/?token=${data?.data?.access}` : "/"}`,
  );
  useKeypress("Enter", () => handleSendMessage());

  const handleSendMessage = async () => {
    const message = messageRef.current?.value;
    const stream = stream_id;
    sendMessage(
      JSON.stringify({
        type: "send_message",
        message,
      }),
    );
    fetch(`/api/comments/`, {
      method: "POST",
      body: JSON.stringify({ stream, message }),
    });

    messageRef.current!.value = "";
  };

  useEffect(() => {
    if (lastMessage) {
      const newMessage = JSON.parse(lastMessage.data);
      if (newMessage.message) {
        setMessageHistory((prevMessages) => [...prevMessages, newMessage]);
      } else if (newMessage.connected_clients) {
        setViewers(newMessage.connected_clients.length);
      }
    }
  }, [lastMessage]);

  const connectionStatus = {
    [ReadyState.CONNECTING]: "Connecting",
    [ReadyState.OPEN]: "Open",
    [ReadyState.CLOSING]: "Closing",
    [ReadyState.CLOSED]: "Closed",
    [ReadyState.UNINSTANTIATED]: "Uninstantiated",
  }[readyState];
  const isAuthenticated = data && !data?.data?.access;

  return (
    <div className="flex-col hidden md:flex min-h-full bg-gray-900 border-l border-gray-800">
      <div className="flex flex-row items-center justify-between p-4 border-b border-gray-800">
        <div className="flex flex-row items-center gap-2">
          <Image
            src={getUserAvatar(username.slice(1))}
            alt="User avatar"
            width={32}
            height={32}
            className="rounded-full"
          />
          <div className="flex flex-col">
            <div className="flex flex-row space-x-2 items-center">
              <span className="text-sm font-bold">{username}</span>
              {isStreaming && <Badge variant="destructive">Live</Badge>}
            </div>
            <span className="text-xs text-gray-500 transition-all duration-300">
              {formatViewers(viewers)} watching
            </span>
          </div>
        </div>
      </div>
      <ul className="flex flex-col flex-grow overflow-y-auto p-2">
        {connectionStatus === "Open" || isLoading ? (
          messageHistory.map((messageData, idx) => (
            <li
              key={idx}
              className="flex flex-row items-center justify-between py-0.5"
            >
              <div className="flex flex-row items-center gap-2">
                <div className="flex flex-row items-center space-x-2">
                  <span
                    className={`text-xs font-bold ${getUsernameColor(messageData.username)}`}
                  >
                    {messageData.username}
                  </span>
                  <span
                    className="text-xs text-gray-500 transition-all duration-300 flex flex-row items-center"
                    dangerouslySetInnerHTML={{
                      __html: messageData.message,
                    }}
                  />
                </div>
              </div>
            </li>
          ))
        ) : error ? (
          <span className="text-sm text-gray-500 p-4">
            An error occurred while connecting to chat.
          </span>
        ) : (
          <span className="text-sm text-gray-500 p-4">
            {connectionStatus}...
          </span>
        )}
      </ul>
      <div className="flex flex-row items-center justify-between gap-2 p-4 border-t border-gray-800 w-max-[120px]">
        <Input
          type="text"
          placeholder="Type message"
          disabled={isAuthenticated}
          ref={messageRef}
        />
        <button
          className="flex flex-row items-center justify-center bg-purple-600 text-white px-4 py-2 rounded-md outline-none"
          disabled={isAuthenticated}
          onClick={() => handleSendMessage()}
        >
          Send
        </button>
      </div>
    </div>
  );
}

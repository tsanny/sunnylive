"use client";
import React, { useState, useEffect, useRef } from "react";
import { getUserAvatar, getUsernameColor } from "@/lib/utils";
import { Badge } from "./ui/badge";
import Image from "next/image";
import { Icons } from "@/components/icons";
import useSWR from "swr";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Input } from "./ui/input";
import useKeypress from "@/hooks/use-key-press";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Label } from "@radix-ui/react-dropdown-menu";

type Message = {
  is_donation: boolean;
  message: string;
  username: string;
  amount?: number;
};

const fetcher = (url: string) =>
  fetch(url, {
    method: "GET",
  }).then((res) => res.json());

export function Chat({
  host_username,
  viewer_username,
  stream_id,
  isStreaming,
}: {
  host_username: string;
  viewer_username?: string;
  stream_id: string;
  isStreaming: boolean;
}) {
  const formatViewers = (viewers: number) => {
    return viewers.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  const [viewers, setViewers] = useState(0);
  const [streamKey, setStreamKey] = useState("");
  const [openDonation, setOpenDonation] = React.useState(false);
  const [openStreamKey, setOpenStreamKey] = React.useState(false);
  const [loading, setLoading] = React.useState(false);
  const [messageHistory, setMessageHistory] = useState<Message[]>([]);
  const [formattedAmount, setFormattedAmount] = useState("");
  const messageRef = useRef<HTMLInputElement>(null);
  const donationMessageRef = useRef<HTMLInputElement>(null);
  const donationAmountRef = useRef<HTMLInputElement>(null);

  const handleAmountFormat = (e: any) => {
    const value = e.target.value.replace(/,/g, "");
    if (!isNaN(value) && value.length <= 10) {
      setFormattedAmount(Number(value).toLocaleString());
    }
  };

  const fetchStreamKey = async () => {
    let response;
    response = await fetch(`/api/streams/${stream_id}/key/`, {
      method: "GET",
    });
    if (response.status === 200) {
      const data = (await response.json()).data;
      setStreamKey(data.stream_key);
    }
  };

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

  const handleSendDonation = async () => {
    const message = donationMessageRef.current?.value;
    const amount = Number(donationAmountRef.current?.value.replace(/,/g, ""));

    const stream = stream_id;
    fetch(`/api/donations/`, {
      body: JSON.stringify({ stream, message, amount }),
    });
    handleCloseDonationDialog();
  };

  const handleOpenStreamKeyDialog = () => {
    setOpenStreamKey(true);
    if (streamKey == "") {
      setLoading(true);
      fetchStreamKey();
      setLoading(false);
    }
  };

  const handleCloseDonationDialog = () => {
    setOpenDonation(false);
    donationMessageRef.current!.value = "";
    setFormattedAmount("");
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
    <>
      <div className="flex-col hidden md:flex min-h-full bg-gray-900 border-l border-gray-800">
        <div className="flex flex-row items-center justify-between p-4 border-b border-gray-800">
          <div className="flex flex-row items-center gap-2">
            <Image
              src={getUserAvatar(host_username)}
              alt="User avatar"
              width={32}
              height={32}
              className="rounded-full"
            />
            <div className="flex flex-col">
              <div className="flex flex-row space-x-2 items-center">
                <span className="text-sm font-bold">{host_username}</span>
                {isStreaming && <Badge variant="destructive">Live</Badge>}
              </div>
              <span className="text-xs text-gray-500 transition-all duration-300">
                {formatViewers(viewers)} watching
              </span>
            </div>
          </div>
        </div>

        {host_username === viewer_username && (
          <>
            <div className="flex flex-row items-center justify-between p-4 border-b border-gray-800">
              <div className="flex justify-between space-x-24">
                <button
                  className="flex flex-row items-center justify-center bg-green-600 text-white px-4 py-1 rounded-md outline-none"
                  disabled={isAuthenticated}
                  onClick={() => setOpenDonation(!openDonation)}
                >
                  <Icons.play className="pr-1" />
                  Start
                </button>
                <button
                  className="flex flex-row items-center justify-center bg-zinc-800 text-white px-4 py-1 rounded-md outline-none"
                  disabled={isAuthenticated}
                  onClick={() => handleOpenStreamKeyDialog()}
                >
                  <Icons.key />
                </button>
              </div>
            </div>
            <AlertDialog open={openStreamKey}>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>{viewer_username} Profile</AlertDialogTitle>
                  <AlertDialogDescription>
                    Here is your stream key, you can use it to stream to your
                    channel.
                    <Label className="mt-4">Stream key</Label>
                    {loading ? (
                      <p>Loading...</p>
                    ) : (
                      <Input
                        type="text"
                        id="streamKey"
                        placeholder="Stream Key"
                        disabled
                        value={streamKey}
                      />
                    )}
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogAction onClick={() => setOpenStreamKey(false)}>
                    Ok
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </>
        )}

        <ul className="flex flex-col flex-grow overflow-y-auto p-2">
          {connectionStatus === "Open" || isLoading ? (
            messageHistory.map((messageData, idx) => (
              <li
                key={idx}
                className="flex flex-row items-center justify-between py-0.5"
              >
                {messageData.is_donation ? (
                  <div className="flex flex-col flex-grow">
                    <div className="flex flex-col bg-emerald-500 p-1.5 rounded-t-md">
                      <span className={`text-xs font-bold text-zinc-900}`}>
                        {messageData.username}
                      </span>
                      <span className={`text-xs font-bold text-gray-50`}>
                        Rp. {Number(messageData.amount).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex flex-row bg-emerald-400 p-1.5 pb-2 rounded-b-md">
                      <span
                        className="text-xs text-gray-800 transition-all duration-300 flex flex-row items-center"
                        dangerouslySetInnerHTML={{
                          __html: messageData.message,
                        }}
                      />
                    </div>
                  </div>
                ) : (
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
                )}
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
        <div className="flex flex-col items-center justify-between gap-2 p-4 border-t border-gray-800 w-max-[120px]">
          <Input
            placeholder="Type message"
            disabled={isAuthenticated}
            ref={messageRef}
          />
          <div className="flex justify-between space-x-24">
            <button
              className="flex flex-row items-center justify-center bg-green-600 text-white px-4 py-1 rounded-md outline-none"
              disabled={isAuthenticated}
              onClick={() => setOpenDonation(!openDonation)}
            >
              $
            </button>
            <button
              className="flex flex-row items-center justify-center bg-purple-600 text-white px-4 py-1 rounded-md outline-none"
              disabled={isAuthenticated}
              onClick={() => handleSendMessage()}
            >
              Send
            </button>
          </div>
        </div>
      </div>
      <AlertDialog open={openDonation}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Send a Donation to {host_username}
            </AlertDialogTitle>
            <AlertDialogDescription>
              Show your support to {host_username} by sending them a donation
              <Label className="mt-4">Amount</Label>
              <Input
                type="text"
                ref={donationAmountRef}
                placeholder="Donation amount"
                value={formattedAmount}
                onChange={handleAmountFormat}
              />
              <Label className="mt-4">Message</Label>
              <Input
                type="text"
                ref={donationMessageRef}
                placeholder="Send a message"
              />
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogAction onClick={() => handleCloseDonationDialog()}>
              Cancel
            </AlertDialogAction>
            <AlertDialogAction
              className="bg-purple-600 text-white"
              onClick={() => handleSendDonation()}
            >
              Send
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

"use client";
import { Chat } from "@/components/chat";
import { VideoPlayer } from "@/components/video-player";
import { useEffect, useState } from "react";

export default function Page({
  params,
}: {
  params: {
    stream_id: string;
  };
}) {
  let stream_id = decodeURIComponent(params.stream_id);

  const [isStreaming, setIsStreaming] = useState(false);
  const [username, setUsername] = useState("");

  useEffect(() => {
    const checkIfStreaming = async () => {
      let response;
      try {
        response = await fetch(`/api/streams/${stream_id}/`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "cache-control": "no-cache",
          },
        });
      } catch (error) {
        setIsStreaming(false);
        return;
      }

      if (response.status === 200) {
        const data = (await response.json()).data;
        setIsStreaming(data.is_started && !data.is_ended);
        setUsername(data.username);
      } else {
        setIsStreaming(false);
      }
    };

    checkIfStreaming();
  }, [stream_id]);

  return (
    <section className="flex flex-col w-full h-full">
      <div className="flex flex-row w-full h-full">
        <VideoPlayer stream_id={stream_id} isStreaming={isStreaming} />
        <Chat
          username={username.trim()}
          stream_id={stream_id}
          isStreaming={isStreaming}
        />
      </div>
      <div className="flex flex-row items-center justify-between w-full px-4 py-2 bg-black/50 md:hidden">
        <div className="flex flex-row items-center justify-center">
          <p className="text-white">{username}</p>
        </div>
      </div>
    </section>
  );
}

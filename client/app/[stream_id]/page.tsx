"use client";
import { Chat } from "@/components/chat";
import { VideoPlayer } from "@/components/video-player";
import { useEffect, useState } from "react";
import { useUser } from "@/context/user.context";
import { toast } from "@/components/ui/use-toast";

export default function Page({
  params,
}: {
  params: {
    stream_id: Readonly<string>;
  };
}) {
  let stream_id = decodeURIComponent(params.stream_id);

  const { user } = useUser();
  const [isStreaming, setIsStreaming] = useState(false);
  const [username, setUsername] = useState("");

  async function startStream() {
    let response;
    try {
      toast({
        title: `Starting the stream...`,
      });
      response = await fetch(`/api/streams/${stream_id}/start/`, {
        method: "GET",
      });
      if (response.status === 200) {
        toast({
          title: `Stream started successfully!`,
        });
        setIsStreaming(true);
      }
    } catch (error) {
      toast({
        title: `Failed to start the stream!`,
        description: (
          <div>An error has occured while trying to start the stream.</div>
        ),
      });
      return;
    }
  }

  async function endStream() {
    let response;
    try {
      toast({
        title: `Ending the stream...`,
      });
      response = await fetch(`/api/streams/${stream_id}/end/`, {
        method: "GET",
      });
      if (response.status === 200) {
        toast({
          title: `Stream ended successfully!`,
        });
        setIsStreaming(false);
      }
    } catch (error) {
      toast({
        title: `Failed to end the stream!`,
        description: (
          <div>An error has occured while trying to end the stream.</div>
        ),
      });
      return;
    }
  }

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
        setIsStreaming(data.is_live);
        setUsername(data.username);
      } else {
        setIsStreaming(false);
      }
    };

    checkIfStreaming();
  }, [stream_id]);

  return (
    <section className="flex flex-col w-full">
      <div className="flex flex-row w-full h-full">
        <VideoPlayer stream_id={stream_id} isStreaming={isStreaming} />
        <Chat
          host_username={username.trim()}
          viewer_username={user?.username}
          stream_id={stream_id}
          isStreaming={isStreaming}
          startStreamHandler={startStream}
          endStreamHandler={endStream}
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

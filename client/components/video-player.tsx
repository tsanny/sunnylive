"use client";
import React, { useRef } from "react";
import HlsPlayer from "react-hls-player";

export function VideoPlayer({
  stream_id,
  isStreaming,
}: {
  stream_id: Readonly<string>;
  isStreaming: Readonly<boolean>;
}) {
  const playerRef = useRef<HTMLVideoElement>(null);

  return (
    <div className="flex flex-col items-center justify-center w-full h-full">
      {isStreaming ? (
        <HlsPlayer
          loop={true}
          width="1920"
          height="1080"
          autoPlay={true}
          controls={true}
          playerRef={playerRef}
          src={`${process.env.NEXT_PUBLIC_HLS_URL}/hls/${stream_id}/index.m3u8`}
          hlsConfig={{
            enableWorker: true,
            maxBufferLength: 1,
            liveBackBufferLength: 0,
            liveSyncDuration: 0,
            liveMaxLatencyDuration: 5,
            liveDurationInfinity: true,
            highBufferWatchdogPeriod: 1,
          }}
          className="w-full h-screen"
        />
      ) : (
        <div className="flex items-center justify-center w-full h-screen bg-black">
          <p className="text-white">Stream is offline</p>
        </div>
      )}
    </div>
  );
}

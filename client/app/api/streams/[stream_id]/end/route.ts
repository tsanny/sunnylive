import { NextRequest, NextResponse } from "next/server";
import { refreshToken } from "../../../refresh-token/refresh";

export async function GET(
  request: NextRequest,
  { params }: { params: { stream_id: string } },
) {
  const API_URL = process.env.API_URL;

  if (!params.stream_id) {
    return NextResponse.json(
      { error: "Stream ID is required" },
      { status: 400 },
    );
  }

  if (!request.cookies.get("sunnylive-auth-token")) {
    return NextResponse.json(
      {
        error: "Not authenticated",
      },
      {
        status: 400,
      },
    );
  }

  const refData = await refreshToken(
    request.cookies.get("sunnylive-auth-refresh-token")!.value,
  );

  const res = await fetch(`${API_URL}/api/streams/${params.stream_id}/end/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${refData.access}`,
      "cache-control": "no-cache",
    },
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail || "Failed to end the stream" },
      { status: res.status },
    );
  }

  return NextResponse.json({ data: data }, { status: 200 });
}

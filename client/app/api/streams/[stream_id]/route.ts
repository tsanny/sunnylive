import { NextRequest, NextResponse } from "next/server";

export async function GET(
  _: NextRequest,
  { params }: { params: { stream_id: string } },
) {
  const API_URL = process.env.API_URL;

  if (!params.stream_id) {
    return NextResponse.json(
      { error: "Stream ID is required" },
      { status: 400 },
    );
  }

  const res = await fetch(`${API_URL}/api/streams/${params.stream_id}/`, {
    method: "GET",
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail || "Failed to fetch stream details" },
      { status: res.status },
    );
  }

  return NextResponse.json({ data: data }, { status: 200 });
}

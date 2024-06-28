import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const body = await request.json();
  let orderId = body.order_id;
  let transactionStatus = body.transaction_status;
  let fraudStatus = body.fraud_status;

  console.log(
    `Transaction notification received. Order ID: ${orderId}. Transaction status: ${transactionStatus}. Fraud status: ${fraudStatus}`,
  );

  let paymentSuccess = false;
  if (transactionStatus == "capture") {
    if (fraudStatus == "accept") {
      paymentSuccess = true;
    }
  } else if (transactionStatus == "settlement") {
    paymentSuccess = true;
  }

  if (paymentSuccess) {
    try {
      const API_URL = process.env.API_URL;
      const res = await fetch(`${API_URL}/api/donations/create/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          order_id: body.order_id,
          status_code: body.status_code,
          gross_amount: body.gross_amount,
          signature_key: body.signature_key,
          ...body.metadata,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        const errorMessage = data.non_field_errors
          ? data.non_field_errors[0]
          : "An error occurred";

        return NextResponse.json(
          { error: errorMessage },
          { status: res.status },
        );
      }

      const data = await res.json();

      return NextResponse.json({ ...data }, { status: res.status });
    } catch (error) {
      throw error;
      return NextResponse.json({ error: "An error occurred" }, { status: 500 });
    }
  }
  return NextResponse.json({ body }, { status: 200 });

  return NextResponse.json({ error: "An error occurred" }, { status: 500 });
}

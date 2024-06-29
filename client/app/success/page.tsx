import { Icons } from "@/components/icons";

export default function Page() {
  return (
    <section className="container grid items-center gap-6 pb-8 pt-6 md:py-10">
      <div className="flex flex-col items-center justify-center gap-y-8">
        <h1 className="text-4xl font-bold">Payment Succeeded</h1>
        <Icons.Check className="pt-2" size={48} />
        <p className="text-gray-500 text-lg">
          We have successfully received your payment. You may now close this
          page.
        </p>
      </div>
    </section>
  );
}

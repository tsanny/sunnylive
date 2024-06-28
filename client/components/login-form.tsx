"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/use-toast";
import { useState } from "react";

import { useUser } from "@/context/user.context";
import { useRouter } from "next/navigation";

const FormSchema = z.object({
  username: z.string(),
  password: z.string().min(8, {
    message: "Password must be at least 8 characters.",
  }),
});

export function LoginForm() {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });

  const { login } = useUser();

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    setError("");
    setLoading(true);

    try {
      const responseData = await login(data.username, data.password);
      router.push("/");
      toast({
        title: `Welcome back ${responseData.user.username}!`,
        description: (
          <div>
            Welcome again to <b>Sunnylive!</b>.
          </div>
        ),
      });
    } catch (err: any) {
      setError(err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Form {...form}>
      <h1 className="text-4xl font-bold">Login to your account</h1>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="sunny32" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input placeholder="••••••••" type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={loading}>
          {loading ? "Logging..." : "Login"}
        </Button>
        {error && <p className="text-red-500">{error}</p>}
      </form>
    </Form>
  );
}

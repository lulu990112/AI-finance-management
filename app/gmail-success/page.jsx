"use client";
import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function GmailSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    if (accessToken) {
      localStorage.setItem("gmail_access_token", accessToken);
      // Set authorization success flag
      localStorage.setItem("gmail_authorized_success", "1");
      // Redirect to homepage
      router.push("/");
    }
  }, [searchParams, router]);

  return <div>Gmail authorization successful, redirecting...</div>;
}

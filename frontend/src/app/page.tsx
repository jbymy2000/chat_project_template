"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import ProtectedRoute from "../components/ProtectedRoute";

export default function Home() {
    const router = useRouter();

    useEffect(() => {
        router.push("/qihang/ai");
    }, [router]);

    return (
        <ProtectedRoute>
            <div className="w-full h-full flex justify-center items-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        </ProtectedRoute>
    );
}

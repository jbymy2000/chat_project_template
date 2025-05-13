"use client";

import { useRouter } from "next/navigation";
import { ReactNode, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";

interface ProtectedRouteProps {
    children: ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
    const { isAuthenticated, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        // 如果认证状态已加载完成且用户未认证，则重定向到登录页面
        if (!isAuthenticated && !loading) {
            router.push("/auth");
        }
    }, [isAuthenticated, loading, router]);

    // 如果正在加载认证状态，显示加载中
    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    // 如果用户已认证，显示子组件
    return isAuthenticated ? <>{children}</> : null;
}

"use client";
import Header from "@/components/header";
import { useAuth } from "@/contexts/AuthContext";
import { useNotification } from "@/contexts/NotificationContext";
import "@ant-design/v5-patch-for-react-19";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function QihangLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { isAuthenticated, loading } = useAuth();
    const router = useRouter();
    const { showNotification } = useNotification();
    const [redirectAttempted, setRedirectAttempted] = useState(false);

    // 检查用户是否已认证
    useEffect(() => {
        // 添加重定向尝试状态检查，防止循环重定向
        if (!loading && !isAuthenticated && !redirectAttempted) {
            setRedirectAttempted(true);
            showNotification("warning", "请先登录");
            router.push("/auth");
        }
    }, [isAuthenticated, loading, router, showNotification, redirectAttempted]);

    if (loading) {
        return <div>加载中...</div>;
    }

    return (
        <div className="flex flex-col h-screen">
            {/* 固定在顶部的Header */}
            <div className="flex-none">
                <Header />
            </div>

            {/* 内容区域，设置为可滚动 */}
            <div className="flex-grow overflow-auto">{children}</div>
        </div>
    );
}

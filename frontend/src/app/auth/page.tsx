"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import LoginForm from "../../components/LoginForm";
import RegisterModal from "../../components/RegisterModal";
import { useAuth } from "../../contexts/AuthContext";

export default function AuthPage() {
    const [showRegisterModal, setShowRegisterModal] = useState(false);
    const { isAuthenticated, login, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        // 如果用户已经认证，重定向到首页或其他页面
        if (isAuthenticated && !loading) {
            router.push("/");
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

    const handleLoginSuccess = (token: string) => {
        login(token);
        router.push("/");
    };

    const handleRegisterSuccess = () => {
        setShowRegisterModal(false);
        // 可以选择显示一个成功消息，然后提示用户登录
        alert("注册成功！请使用您的新账号登录");
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <h1 className="text-center text-3xl font-extrabold text-gray-900">
                        欢迎使用我们的平台
                    </h1>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        请登录以继续访问
                    </p>
                </div>

                <LoginForm
                    onLoginSuccess={handleLoginSuccess}
                    onRegisterClick={() => setShowRegisterModal(true)}
                />

                {showRegisterModal && (
                    <RegisterModal
                        isOpen={showRegisterModal}
                        onClose={() => setShowRegisterModal(false)}
                        onSuccess={handleRegisterSuccess}
                    />
                )}
            </div>
        </div>
    );
}

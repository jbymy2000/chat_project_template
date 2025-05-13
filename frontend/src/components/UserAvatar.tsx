"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useAuth } from "../contexts/AuthContext";

interface UserAvatarProps {
    className?: string;
}

export default function UserAvatar({ className = "" }: UserAvatarProps) {
    const { user, logout } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);
    const avatarRef = useRef<HTMLDivElement>(null);
    const router = useRouter();

    // 获取用户名首字母或第一个字符
    const getInitials = () => {
        if (!user) return "?";
        return user.username.charAt(0).toUpperCase();
    };

    // 根据用户名生成随机颜色（保持一致性）
    const getBackgroundColor = () => {
        if (!user) return "#6c757d";
        let hash = 0;
        for (let i = 0; i < user.username.length; i++) {
            hash = user.username.charCodeAt(i) + ((hash << 5) - hash);
        }
        const hue = Math.abs(hash) % 360;
        return `hsl(${hue}, 70%, 50%)`;
    };

    const handleLogout = () => {
        logout();
        setIsMenuOpen(false);
        router.push("/auth");
    };

    // 处理点击头像外部关闭菜单
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                menuRef.current &&
                !menuRef.current.contains(event.target as Node) &&
                avatarRef.current &&
                !avatarRef.current.contains(event.target as Node)
            ) {
                setIsMenuOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    if (!user) {
        return (
            <div
                className={`rounded-full w-10 h-10 flex items-center justify-center bg-gray-300 text-gray-600 cursor-pointer ${className}`}
                onClick={() => router.push("/auth")}
            >
                ?
            </div>
        );
    }

    return (
        <div className="relative">
            <div
                ref={avatarRef}
                className={`rounded-full w-10 h-10 flex items-center justify-center text-white font-medium cursor-pointer ${className}`}
                style={{ backgroundColor: getBackgroundColor() }}
                onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
                {getInitials()}
            </div>

            {isMenuOpen && (
                <div
                    ref={menuRef}
                    className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg z-50"
                >
                    <div className="p-4 border-b border-gray-100">
                        <p className="text-sm font-medium text-gray-900">
                            {user.username}
                        </p>
                        {user.email && (
                            <p className="text-xs text-gray-500 mt-1">
                                {user.email}
                            </p>
                        )}
                    </div>
                    <div className="py-1">
                        <button
                            onClick={handleLogout}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                            退出登录
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

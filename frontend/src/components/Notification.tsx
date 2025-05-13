"use client";

import { useEffect, useState } from "react";

export type NotificationType = "success" | "error" | "info" | "warning";

interface NotificationProps {
    type: NotificationType;
    message: string;
    duration?: number;
    onClose?: () => void;
}

export default function Notification({
    type,
    message,
    duration = 3000,
    onClose,
}: NotificationProps) {
    const [isVisible, setIsVisible] = useState(true);
    const [isEntering, setIsEntering] = useState(true);

    useEffect(() => {
        // 设置进入动画结束
        const enterTimer = setTimeout(() => {
            setIsEntering(false);
        }, 300);

        // 设置自动关闭计时器
        let exitTimer: NodeJS.Timeout;
        if (duration > 0) {
            exitTimer = setTimeout(() => {
                setIsVisible(false);
                if (onClose) onClose();
            }, duration);
        }

        return () => {
            clearTimeout(enterTimer);
            if (exitTimer) clearTimeout(exitTimer);
        };
    }, [duration, onClose]);

    if (!isVisible) return null;

    const bgColors = {
        success: "bg-green-100 border-green-400 text-green-700",
        error: "bg-red-100 border-red-400 text-red-700",
        info: "bg-blue-100 border-blue-400 text-blue-700",
        warning: "bg-yellow-100 border-yellow-400 text-yellow-700",
    };

    const icons = {
        success: (
            <svg
                className="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                ></path>
            </svg>
        ),
        error: (
            <svg
                className="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                ></path>
            </svg>
        ),
        info: (
            <svg
                className="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zm-1 7a1 1 0 01-1-1v-3a1 1 0 112 0v3a1 1 0 01-1 1z"
                    clipRule="evenodd"
                ></path>
            </svg>
        ),
        warning: (
            <svg
                className="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                ></path>
            </svg>
        ),
    };

    // 动画类名
    const animationClass = isEntering ? "animate-slide-in-down" : "";

    return (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
            <div
                className={`${bgColors[type]} ${animationClass} border px-4 py-3 rounded flex items-center max-w-md shadow-lg transition-all duration-300`}
                role="alert"
                style={{ minWidth: "300px" }}
            >
                <div className="mr-3">{icons[type]}</div>
                <div>{message}</div>
                <button
                    className="ml-auto"
                    onClick={() => {
                        setIsVisible(false);
                        if (onClose) onClose();
                    }}
                >
                    <svg
                        className="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            fillRule="evenodd"
                            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                            clipRule="evenodd"
                        ></path>
                    </svg>
                </button>
            </div>
        </div>
    );
}

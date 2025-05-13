"use client";

import { createContext, ReactNode, useContext, useState } from "react";
import Notification, { NotificationType } from "../components/Notification";

interface NotificationContextType {
    showNotification: (
        type: NotificationType,
        message: string,
        duration?: number
    ) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(
    undefined
);

export function NotificationProvider({ children }: { children: ReactNode }) {
    const [notification, setNotification] = useState<{
        type: NotificationType;
        message: string;
        duration: number;
        id: number;
    } | null>(null);

    const showNotification = (
        type: NotificationType,
        message: string,
        duration: number = 3000
    ) => {
        // 生成唯一ID以处理多个通知的情况
        const id = Date.now();
        setNotification({ type, message, duration, id });
    };

    const handleClose = () => {
        setNotification(null);
    };

    return (
        <NotificationContext.Provider value={{ showNotification }}>
            {children}
            {notification && (
                <Notification
                    key={notification.id}
                    type={notification.type}
                    message={notification.message}
                    duration={notification.duration}
                    onClose={handleClose}
                />
            )}
        </NotificationContext.Provider>
    );
}

export function useNotification() {
    const context = useContext(NotificationContext);
    if (context === undefined) {
        throw new Error("useNotification 必须在 NotificationProvider 内部使用");
    }
    return context;
}

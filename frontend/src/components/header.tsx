import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useState } from "react";
import ProfileInfo from "./ProfileInfo";
import ProfileModal from "./ProfileModal";
import UserAvatar from "./UserAvatar";

// 定义用户信息类型
interface UserInfo {
    name?: string;
    avatar?: string;
    email?: string;
    [key: string]: unknown;
}

interface HeaderProps {
    logo?: string;
    info?: string;
    onSessionChange?: (session: string) => void;
    isLoading?: boolean;
    userInfo?: UserInfo;
    onUserInfoChange?: (userInfo: UserInfo) => void;
}

export default function Header({
    logo = "/qihanglogo.png",
    info = "XXAI",
}: HeaderProps) {
    const pathname = usePathname();
    const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
    // 添加刷新触发器 - 每次更新用户资料后会+1
    const [profileRefreshTrigger, setProfileRefreshTrigger] = useState(0);

    const menuItems = [
        { name: "问AI", path: "/qihang/ai" },
        { name: "自己查", path: "/qihang/data/recommendation" },
    ];

    // 处理用户资料更新后的回调
    const handleProfileUpdate = useCallback(() => {
        // 增加刷新触发器，使ProfileInfo组件重新获取数据
        setProfileRefreshTrigger((prev) => prev + 1);
        // 关闭弹窗
        setIsProfileModalOpen(false);
    }, []);

    return (
        <header className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center">
                        <Link href="/" className="flex items-center">
                            <Image
                                src={logo}
                                alt="Company Logo"
                                width={60}
                                height={60}
                                className="h-12 w-12 rounded-full object-cover"
                            />
                            <span className="ml-2 text-xl font-semibold text-gray-900">
                                {info}
                            </span>
                        </Link>
                    </div>
                    <nav className="flex space-x-8">
                        {menuItems.map((item) => (
                            <Link
                                key={item.path}
                                href={item.path}
                                className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${
                                    pathname === item.path
                                        ? "text-blue-600 border-b-2 border-blue-600"
                                        : "text-gray-500 hover:text-gray-700 hover:border-gray-300"
                                }`}
                            >
                                {item.name}
                            </Link>
                        ))}
                    </nav>
                    <div className="flex items-center space-x-4">
                        {/* 使用ProfileInfo组件显示用户信息，传入刷新触发器 */}
                        <ProfileInfo
                            onClick={() => setIsProfileModalOpen(true)}
                            refreshTrigger={profileRefreshTrigger}
                        />

                        {/* 用户头像 */}
                        <UserAvatar />
                    </div>
                </div>
            </div>

            {/* 使用ProfileModal组件，传入成功保存的回调函数 */}
            <ProfileModal
                isOpen={isProfileModalOpen}
                onClose={() => setIsProfileModalOpen(false)}
                onSuccess={handleProfileUpdate}
            />
        </header>
    );
}

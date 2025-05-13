import { useAuth } from "@/contexts/AuthContext";


// 兼容层，将新的认证系统包装为旧的useUser hook接口
export default function useUser() {
    const { user: authUser } = useAuth();
    
    // 转换新的用户对象到旧接口格式
    const user = authUser ? {
        uid: authUser.username, // 使用username作为旧系统中的uid
    } : null;

    return { user };
}
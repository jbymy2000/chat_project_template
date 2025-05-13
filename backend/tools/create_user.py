import sys
import os
import asyncio
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService
from dao.database import Database
from services.profile_service import ProfileService

async def create_test_user():
    try:
        # 初始化数据库连接池
        await Database.get_pool()
        
        # 创建测试用户
        user = await AuthService.create_user(
            username='test_user',
            password='test123',
            email='test@example.com'
        )
        print(f'创建用户成功: {user}')
    except Exception as e:
        print(f'创建用户失败: {str(e)}')
    finally:
        # 关闭数据库连接池
        await Database.close_pool()

async def create_test_profile():
    try:
        # 初始化数据库连接池
        await Database.get_pool()
        
        # 创建测试用户档案
        profile = await ProfileService.create_profile(
            user_id=4,  # 测试用户的ID
            province="北京",
            score=600,
            subject_choice=["物理", "化学"]
        )
        print(f'创建用户档案成功: {profile}')
    except Exception as e:
        print(f'创建用户档案失败: {str(e)}')
        print('完整错误栈:')
        traceback.print_exc()
    finally:
        # 关闭数据库连接池
        await Database.close_pool()

if __name__ == '__main__':
    # asyncio.run(create_test_user())
    asyncio.run(create_test_profile()) 

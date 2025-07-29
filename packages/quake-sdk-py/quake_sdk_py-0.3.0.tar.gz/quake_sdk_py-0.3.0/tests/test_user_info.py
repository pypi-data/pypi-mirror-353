import pytest
import pprint

from quake_sdk.client import QuakeClient
from quake_sdk.exceptions import QuakeAuthException
from quake_sdk.models import UserInfoResponse, UserRole

# API_KEY is implicitly used by the 'client' fixture from conftest.py
# We can reference it directly if needed for assertions against the response,
# or rely on the fixture to handle the key.
# For clarity in tests that check the returned token, explicitly using it might be better.
# from ..conftest import API_KEY # This relative import won't work directly in pytest execution path from root
# Instead, we can access it via client.api_key if needed, or hardcode for assertion if it's static for tests.

class TestUserInfo:
    def test_get_user_info_success(self, client: QuakeClient):
        """Tests successful retrieval of user information."""
        response = client.get_user_info()

        # Print user information for verification using pprint
        print("\nUser Info Response (pprint):")
        pprint.pprint(response.model_dump())

        assert response is not None
        assert response.code == 0
        assert response.message == "Successful."
        assert response.data is not None
        
        # Assertions for UserInfoData
        user_data = response.data
        assert isinstance(user_data.id, str)
        assert isinstance(user_data.credit, int)
        assert user_data.token == client.api_key # API returns the key in user info
        assert user_data.user is not None
        
        # Assertions for User
        user = user_data.user
        assert isinstance(user.id, str)
        assert isinstance(user.username, str)
        assert isinstance(user.fullname, str)
        # email可能为None，不再强制要求非空
        assert user.email is None or isinstance(user.email, str)
        
        # 用户名应该非空
        assert user.username != ""

        # 角色验证
        assert user_data.role is not None
        assert len(user_data.role) > 0
        assert isinstance(user_data.role[0], UserRole)
        assert isinstance(user_data.role[0].fullname, str)
        
        # 验证积分相关字段
        assert isinstance(user_data.persistent_credit, int)
        
        # 验证其他字段
        # 使用 hasattr 检查字段是否存在，因为API响应可能不包含所有字段
        if hasattr(user_data, 'banned'):
            assert isinstance(user_data.banned, bool)
        assert isinstance(user_data.ban_status, str)
        assert isinstance(user_data.source, str)
        assert isinstance(user_data.personal_information_status, bool)


    def test_get_user_info_auth_error(self, invalid_client: QuakeClient):
        """Tests authentication error when fetching user info with an invalid key."""
        with pytest.raises(QuakeAuthException) as exc_info:
            invalid_client.get_user_info()
        # Depending on Quake's specific error code for invalid token for this endpoint
        # it might be u3011 (permission) or another.
        # The client maps u3011 to QuakeAuthException.
        # If the response body is not JSON (e.g., HTML login page), api_code will be None.
        assert exc_info.value.api_code is None or exc_info.value.api_code == "u3011"
        assert exc_info.value.response_status_code == 401 # Or 403, depends on API
        
    def test_user_info_with_vip_role(self, client: QuakeClient):
        """测试VIP用户的角色信息处理"""
        response = client.get_user_info()
        if response.data:
            # 检查角色
            if len(response.data.role) > 1:
                print(f"\n该用户有多个角色:")
                for role in response.data.role:
                    print(f"  - {role.fullname} (优先级: {role.priority}, 积分: {role.credit})")
            
            # 检查扩展字段（如果存在）
            if hasattr(response.data, 'role_validity') and response.data.role_validity:
                print(f"\n角色有效期:")
                for role_name, validity in response.data.role_validity.items():
                    if validity and hasattr(validity, 'remain_days'):
                        print(f"  - {role_name}: 剩余 {validity.remain_days} 天")

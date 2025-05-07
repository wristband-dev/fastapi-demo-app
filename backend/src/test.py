from wristband.models import SessionData

session_data = SessionData(
    is_authenticated=True,
    user_info={
        "tenantId": "123",
        "userId": "123",
        "metadata": {
            "test": "test"
        }
    },
    refresh_token="123",
    access_token="123",
    expires_at=123,
    tenant_domain_name="test",
    tenant_custom_domain="test",
)

print(session_data.to_session_init_data())
from testdata.test_model import UserData


def generate_user_data(index: int = 1) -> dict:
    """Генерация уникального пользователя по индексу."""
    return UserData(
        login=f'test_user_{index}',
        password=f'secure_pass_{index}',
        first_name='Test',
        last_name=f'User{index}'
    ).dict()

import shortuuid
from authentication.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class AuthHelper:

    @staticmethod
    def create_username(email):
        try:
            total_retries = 5
            email_part = email.rsplit('@', 1)
            clean_email_part = "".join(
                char for char in email_part[0][:20] if char.isalnum())
            for i in range(0, total_retries):
                uuid = shortuuid.uuid()
                username = f'{clean_email_part}_{uuid}'.lower()

                user = User.objects.filter(username=username)
                if user.exists():
                    continue
                else:
                    return username
            raise Exception("Max retries exhausted.")

        except Exception as e:
            raise Exception("Error while creating the username.") from e

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user=user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }


def validation_error_handler(errors: dict):
    key = list(errors.keys())[0]
    error = errors[key]

    if type(error) == list:
        message = f'{key}: {error[0]}'
    else:
        message = f'{key}: {error}'
    return message
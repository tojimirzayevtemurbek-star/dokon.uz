from django.contrib.auth.password_validation import (
    CommonPasswordValidator,
    MinimumLengthValidator,
    NumericPasswordValidator,
    UserAttributeSimilarityValidator,
)
from django.core.exceptions import ValidationError


class UzbekUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "Parolingiz shaxsiy ma'lumotlaringizga (ism, login va h.k.) juda o'xshash.",
                code="password_too_similar",
            )

    def get_help_text(self):
        return "Parolingiz shaxsiy ma'lumotlaringizga juda o'xshash bo'lmasligi kerak."


class UzbekMinimumLengthValidator(MinimumLengthValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                f"Parolingiz kamida {self.min_length} ta belgidan iborat bo'lishi kerak.",
                code="password_too_short",
            )

    def get_help_text(self):
        return f"Parolingiz kamida {self.min_length} ta belgidan iborat bo'lishi kerak."


class UzbekCommonPasswordValidator(CommonPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "Bu parol juda keng tarqalgan.",
                code="password_too_common",
            )

    def get_help_text(self):
        return "Parolingiz keng tarqalgan parol bo'lmasligi kerak."


class UzbekNumericPasswordValidator(NumericPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "Parolingiz faqat raqamlardan iborat bo'lishi mumkin emas.",
                code="password_entirely_numeric",
            )

    def get_help_text(self):
        return "Parolingiz faqat raqamlardan iborat bo'lmasligi kerak."

import pytest

from app.domain.iam.exceptions import InvalidEmailError, InvalidPhoneNumberError
from app.domain.iam.value_objects import Email, PasswordHash, PhoneNumber


class TestEmail:
    @pytest.mark.parametrize("valid", ["a@b.com", "user.name+tag@sub.example.org", "x@y.io"])
    def test_valid_email_accepted(self, valid):
        assert Email(valid).value == valid

    @pytest.mark.parametrize("invalid", ["", "no-at-sign", "a@b", "@missing.local", "a b@c.com"])
    def test_invalid_email_raises(self, invalid):
        with pytest.raises(InvalidEmailError):
            Email(invalid)


class TestPhoneNumber:
    @pytest.mark.parametrize("valid", ["+989123456789", "021-12345678", "+1 (415) 555-0132"])
    def test_valid_phone_accepted(self, valid):
        assert PhoneNumber(valid).value == valid

    @pytest.mark.parametrize("invalid", ["", "abc", "123"])
    def test_invalid_phone_raises(self, invalid):
        with pytest.raises(InvalidPhoneNumberError):
            PhoneNumber(invalid)


class TestPasswordHash:
    def test_wraps_value(self):
        assert PasswordHash("bcrypt:xyz").value == "bcrypt:xyz"

    def test_value_objects_are_immutable(self):
        assert Email("a@b.com") == Email("a@b.com")

import pytest
from app.auth.services.otp import OTPService



def test_generate_otp_length():
    otp = OTPService.generate_otp(length=6)

    assert len(otp) == 6
    assert otp.isdigit()


def test_generate_otp_is_different_each_time():
    otp1 = OTPService.generate_otp()
    otp2 = OTPService.generate_otp()

    if otp1 == otp2:
        otp2 = OTPService.generate_otp()

    assert otp1 != otp2


def test_hash_token_consistency():
    token = "123456"
    
    hashed1 = OTPService.hash_token(token)
    hashed2 = OTPService.hash_token(token)

    assert hashed1 == hashed2
    assert isinstance(hashed1, str)


def test_verify_input_token_valid():
    input_token = "123456"

    stored_hash = OTPService.hash_token(input_token)

    result = OTPService.verify_input_token(input_token, stored_hash, expected_length=6)
    assert result is True


def test_verify_input_token_format():
    invalid_token = "a" * 64

    with pytest.raises(ValueError):
        OTPService.verify_input_token("123xyz", invalid_token, expected_length=6)
        

def test_verify_wrong_input_token():
    token = "001122"
    wrong = "001133"

    hashed = OTPService.hash_token(token)

    result = OTPService.verify_input_token(wrong, hashed, expected_length=6)
    assert result is False
def test_verify_email_txt_render(jinja_env):

    context = {
        "user_name": "TestUser",
        "otp_code": "123456",
        "expire_minutes": 10
    }

    template = jinja_env.get_template("email/verify_email.txt")
    output = template.render(context)

    assert "Verify Your Email Address" in output
    assert "Hi TestUser!" in output
    assert "Your verification code is: 123456" in output
    assert "This code will expire in 10 minutes." in output
    assert "The AuthPad Team" in output


def test_verify_email_html_render(jinja_env):

    context = {
        "user_name": "TestUser",
        "otp_code": "123456",
        "expire_minutes": 10
    }

    template = jinja_env.get_template("email/verify_email.html")
    output = template.render(context)

    assert "Verify Your Email Address" in output
    assert "Hi TestUser!" in output
    assert "Your verification code is: <strong>123456</strong>" in output
    assert "This code will expire in 10 minutes." in output
    assert "The <strong>AuthPad</strong> Team" in output
import os, traceback
import telnyx
import math
import random

telnyx.APIKey = os.environ.get("TELNYX_API_KEY", None)
our_telnyx_number = os.environ.get("TELNYX_PHONE_NUMBER", None)


def send_sms(destination):
    destination_number = destination
    digits = "0123456789"
    otp_size = 6
    otp = ""
    for interation in range(otp_size):
        otp += digits[math.floor(random.random() * 10)]
    try:
        telnyx.Message.create(from_=our_telnyx_number, to=destination_number, text="Hello, The OTP generated for "
                                                                               "verification purpose is " + otp)
    except Exception as e:
        otp = ""
        print("Exception encountered while generating the OTP!")
        traceback.print_exc()
    return otp

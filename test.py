from requests import Session
import threading

class TEST():
    def __init__ (self):
        self.session = Session()
        self.session.headers = {
            "x-api-key": "91e894522aa3ef0248aaef99864682782099156d817fbdab3981f79a000c37dc"
        }
        self.base_url = "https://b9i590vc4i.execute-api.eu-west-1.amazonaws.com/dev"
    
    def get_user (self):
        res = self.session.get(
            url = f"{self.base_url}/manageUser"
        )
        print("email is :",  res.text)
        # res.raise_for_status()

    def get_token (self, email):
        print("get_token")
        res = self.session.post(
            url = f"{self.base_url}/getToken",
            json = { "email": email }
        )
        print("email:", email, "token is :", res.text)
        # res.raise_for_status()

test = TEST()
# test.get_user()
# test.get_token("email7@mail.fr")

def thread():
    threads = []
    emails = ["email123@mail.fr", "email231@mail.fr", "email312@mail.fr"]

    for email in emails:
        t = threading.Thread(target=test.get_token, args=(email,))
        t.start()
        threads.append(t)

thread()

# try:
#     res = requests.post(
#         url = "https://b9i590vc4i.execute-api.eu-west-1.amazonaws.com/dev/manageUser",
#         headers = {
#             "x-api-key": "ba0d62b9-542a-481b-8835-c0a2b4bc1de8"
#         }
#     )
#     res.raise_for_status()
#     print('1', res.text, res.status_code)

# except HTTPError as error:
#     print(error.response.status_code, error.response.text)
    
# except Exception as error:
#     print("2", error)
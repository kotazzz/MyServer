import requests  # type: ignore


def register_user(user, password, point):
    url = f"https://kotaz.ddnsfree.com:24555/api/auth/{point}"
    data = {"user": user, "password": password}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            token = response.text
            print(f"Token received ({point}):", token)
        else:
            print(f"Failed to {point} user:", response.text)
    except Exception as e:
        print(f"Error occurred during {point}:", e)


# Пример использования
username = "example_user"
password = "example_password"
# register_user(username, password, "register")
register_user(username, password, "login")

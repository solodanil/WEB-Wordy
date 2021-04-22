from requests import get

print(get('http://127.0.0.1:8080/api/v1/user/281317152').json())

print(get('http://127.0.0.1:8080/api/v1/user/212345').json())
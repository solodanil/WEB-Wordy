from requests import get, post
from data import db_session
from data.user import User
#print(get('http://127.0.0.1:8080/api/v1/user/281317152').json())

#print(get('http://127.0.0.1:8080/api/v1/user/212345').json())

#print(get('http://127.0.0.1:8080/api/v1/vocabulary/281317152').json())
print(-1)

print(get('http://127.0.0.1:8080/api/v1/vocabulary/281317152').json())

#print(get('http://127.0.0.1:8080/api/v1/vocabulary/281317152').json())

#print(get('http://127.0.0.1:8080/api/v1/vocabulary/123').json())
print(0)

print(post('http://127.0.0.1:8080/api/v1/vocabulary/281317152', json={'word_id': 4}).json())
print(1)
print(get('http://127.0.0.1:8080/api/v1/vocabulary/281317152').json())

print(2)
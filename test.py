from requests import get
from data import db_session
from data.user import User
#print(get('http://127.0.0.1:8080/api/v1/user/281317152').json())

#print(get('http://127.0.0.1:8080/api/v1/user/212345').json())

#print(get('http://127.0.0.1:8080/api/v1/vocabulary/281317152').json())

#print(get('http://127.0.0.1:8080/api/v1/vocabulary/281317152').json())

#print(get('http://127.0.0.1:8080/api/v1/vocabulary/281317152').json())

#print(get('http://127.0.0.1:8080/api/v1/vocabulary/123').json())


session = db_session.create_session()
user = session.query(User).filter(User.social_id == 1).first()
print(user)
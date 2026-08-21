from sqlalchemy.orm import Session
try:
    from passlib.context import CryptContext  # type: ignore[import-not-found]
except ImportError as exc:
    raise RuntimeError("Install the 'passlib[bcrypt]' dependency to use password hashing.") from exc
from ..entities.user import User
from ..services.schemas import UserCreate, UserLogin
from ..exceptions.user_exceptions import UserAlreadyExistsError, InvalidCredentialsError
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
  def __init__(self, db:Session):
    self.db = db

  def hash_password(self, password: str) -> str:
    return pwd_context.hash(password)

  def verify_password(self, plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

  def create_user(self, user_data: UserCreate) -> User:
    existing_user = self.db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
      raise UserAlreadyExistsError(user_data.email)

    hashed_password = self.hash_password(user_data.password)

    user = User(
      id = uuid.uuid4(),
      email = user_data.email,
      first_name = user_data.first_name,
      last_name = user_data.last_name,
      password = hashed_password
    
    )

    self.db.add(user)
    self.db.commit()
    self.db.refresh(user)
    return user

  def authenticate_user(self, user_data: UserLogin) -> User:

    user = self.db.query(User).filter(User.email == user_data.email).first()

    if not user:
      raise InvalidCredentialsError()

    if not self.verify_password(user_data.password, user.password):
      raise InvalidCredentialsError()

    return user

  def get_user_by_id(self, user_id: uuid.UUID) -> User:
    return self.db.query(User).filter(User.id == user_id).first() 

  def get_user_by_email(self, email: str) -> User:
    return self.db.query(User).filter(User.email == email).first()
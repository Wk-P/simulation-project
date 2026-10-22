# Simulation Project UML

用户、会话、认证三个领域的结构图。当前代码快照：src/ 下 services、repositories、models、schemas、routers 五层。

[依赖方向](#deps)[类与模块](#class)[数据表](#er) [登录流程](#login)[带 token 请求](#request)[刷新与登出](#refresh)[接口](#routes)

usersessionauth

## 依赖方向

auth 同时依赖 user 和 session；user 与 session 互不依赖。箭头表示“使用”。

```mermaid
flowchart TB
  subgraph R["routers（只处理 HTTP）"]
    rreg["register.py"]
    rlogin["login.py"]
    rme["me.py"]
    rtoken["token.py"]
    rdeps["deps.pyget_current_user"]
  end
  subgraph A["services/auth"]
    alogin["login.pyuser_login_svc"]
    aauth["authenticate.pytoken_authenticate"]
  end
  subgraph U["services/user"]
    ureg["register.py"]
    ume["me.pyuser_get_me"]
    upw["password.py"]
  end
  subgraph S["services/session"]
    ssess["session.pystart / refresh / end"]
    stok["token.pyencode / decode"]
  end
  subgraph REPO["repositories"]
    urepo["UserRepository"]
    srepo["SessionRepository"]
  end
  rreg --> ureg
  rlogin --> alogin
  rme --> ume
  rme --> rdeps
  rdeps --> aauth
  rtoken --> ssess
  alogin --> upw
  alogin --> ssess
  alogin --> urepo
  aauth --> stok
  aauth --> urepo
  ureg --> upw
  ureg --> urepo
  ssess --> stok
  ssess --> srepo
```

## 类与模块

函数式的 service 用 module 构造型表示，Repository 和 Model 是真正的类。

```mermaid
classDiagram
  direction LR
  class UserRepository {
    +exists_by_username(username) bool
    +create(user) UserModel
    +get_user_by_id(id) UserModel
    +get_user_by_username(username) UserModel
  }
  class SessionRepository {
    +get_by_id(session_id) SessionModel
    +create(session) SessionModel
    +revoke(session, revoked_at)
    +revoke_all_by_user(user_id, revoked_at)
  }
  class UserModel {
    +int id
    +str username
    +str password_hash
    +str email
    +bool admin
    +bool staff
    +bool active
  }
  class SessionModel {
    +str id
    +int user_id
    +str refresh_token_hash
    +datetime expires_at
    +datetime revoked_at
    +datetime created_at
  }
  class session_service {
    <>
    +start_session(user_id, repo) AuthTokens
    +refresh_session(refresh_token, repo) AuthTokens
    +end_session(refresh_token, repo)
    -_get_valid_session(refresh_token, repo)
  }
  class token_service {
    <>
    +encode_token(user_id, type, expires_at, jti)
    +encode_access_token(user_id)
    +decode_token(token, expected_type) dict
  }
  class login_service {
    <>
    +login(username, password, repo) UserModel
    +user_login_svc(req, user_repo, session_repo)
  }
  class authenticate_service {
    <>
    +token_authenticate(token, repo) UserModel
  }
  class AuthTokens {
    +str access_token
    +str refresh_token
  }
  UserRepository ..> UserModel : 读写
  SessionRepository ..> SessionModel : 读写
  SessionModel "many" --> "1" UserModel : user_id
  session_service ..> SessionRepository
  session_service ..> token_service
  session_service ..> AuthTokens : 返回
  login_service ..> UserRepository
  login_service ..> session_service
  authenticate_service ..> UserRepository
  authenticate_service ..> token_service
```

## 数据表

一个用户可以有多条会话，每条会话对应一台设备的一次登录。refresh token 里的 jti 等于 sessions.id。

```mermaid
erDiagram
  users ||--o{ sessions : "拥有"
  users {
    int id PK
    string username UK
    string password_hash
    string email
    bool admin
    bool staff
    bool active
  }
  sessions {
    string id PK "等于 refresh token 的 jti"
    int user_id FK
    string refresh_token_hash
    datetime expires_at
    datetime revoked_at "为空表示有效"
    datetime created_at
  }
```

## 登录流程

密码验证在 user 一侧，建会话和签发 token 在 session 一侧，auth 把两步接起来。

```mermaid
sequenceDiagram
  autonumber
  participant C as 客户端
  participant R as routers/login
  participant L as auth/login
  participant UR as UserRepository
  participant S as session/session
  participant T as session/token
  participant SR as SessionRepository
  C->>R: POST /login/user
  R->>L: user_login_svc
  L->>UR: get_user_by_username
  UR-->>L: UserModel
  L->>L: password_verify
  L->>S: start_session(user_id)
  S->>T: encode_token(refresh, jti=session_id)
  T-->>S: refresh_token
  S->>SR: create(SessionModel 含 token 哈希)
  S->>T: encode_access_token
  T-->>S: access_token
  S-->>L: AuthTokens
  L-->>R: LoginUserResponse
  R-->>C: 200 用户信息和 tokens
```

## 带 token 的请求

只验证 access token 的签名和过期时间，不查 sessions 表，所以每次请求只有一次用户查询。

```mermaid
sequenceDiagram
  autonumber
  participant C as 客户端
  participant D as routers/deps
  participant A as auth/authenticate
  participant T as session/token
  participant UR as UserRepository
  participant H as routers/me
  C->>D: GET /me（Authorization: Bearer）
  D->>A: token_authenticate
  A->>T: decode_token(access)
  T-->>A: payload（sub）
  A->>UR: get_user_by_id
  UR-->>A: UserModel
  A-->>D: UserModel（active）
  D->>H: current user
  H-->>C: 200 GetMeResponse
  Note over D,C: 任一步失败，deps 返回 401
```

## 刷新与登出

每个 refresh token 只能用一次。已作废的 token 再次出现，说明可能被盗，该用户的全部会话一并撤销。

```mermaid
stateDiagram-v2
  [*] --> Active : start_session
  Active --> Revoked : refresh_session（换新会话）
  Active --> Revoked : end_session（登出）
  Active --> Expired : 超过 expires_at
  Revoked --> AllRevoked : 旧 token 被再次使用
  Expired --> [*]
  Revoked --> [*]
  AllRevoked --> [*]
  note right of AllRevoked
    revoke_all_by_user
    该用户所有会话作废
  end note
```

## 接口

main.py 目前只注册了 register 和 login，me 与 token 两个 router 还没有加进去。

| 方法 | 路径 | Router | Service | 已注册 |
| --- | --- | --- | --- | --- |
| POST | `/register/user` | register.py | user | 是 |
| POST | `/register/staff` | register.py | user | 是 |
| POST | `/register/admin` | register.py | user | 是 |
| POST | `/login/user` | login.py | auth | 是 |
| GET | `/me` | me.py | user + auth | 否 |
| POST | `/token/refresh` | token.py | session | 否 |
| POST | `/token/logout` | token.py | session | 否 |
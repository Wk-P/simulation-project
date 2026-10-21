# JWT
## 为什么需要JWT？
如果只有HTTP的请求，Server不认识Client，更不会知道是否登录了。因为HTTP无状态，你可以登录N次，也只是出发了HTTP Request 和 Response

## JWT 凭证
登录成功后 JWT 系统会有一个凭证，后续你就不需要每次都输入密码，拿着凭证就可以继续访问登录后才可以访问的内容了。

这个凭证就是 **access token**

## JWT 流程
真实的 JWT 并不完全是单纯拿个凭证，一般有两个阶段。

第一个阶段叫鉴权 Authentication
- 用户名 + 密码 -> 验证身份

第二阶段一般叫 Authenticated Requests
- token
持续证明身份

## access token
当登录成功后，access token就会通过response 发给客户端。再次需要的时候，客户端需要在HTTP请求头中加入
```json
{
    "Authorization": "Bearer <access_token>"
}
```
此时后端就会收到access_token去鉴权，用来知道token是谁

token 通常分为
```text
Header.Payload.Signature
```
中间的payload 可能会包含
- sub = user_id
- exp = 过期时间



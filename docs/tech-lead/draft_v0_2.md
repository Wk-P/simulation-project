# draft v0.2
你需要提交 Technical Design v0.2。这次不要追求长，我要的是结构清楚、每个技术选择都有理由。至少重新回答这 7 项：
1. Tech Stack：FastAPI 可以保留；明确持久数据库；重新考虑 JWT/Cookie/Session；Redis 只有能说清解决什么问题才能留下。
    JWT 这里 JWT 只做action部分发出请求时需要的token验证，登录交给 cookie/session 控制；当用户下线或者被重置密码，token进入blacklist自动失效，cookie/session也做相应清理。
    redis是我没有考虑好，但是因为运维人员会在不同地方登录，为了防止断电网络原因等问题，数据库还需要异地备份，所以我建议使用docker-redis来保存数据，这样redis主从哨兵模式可以保证数据不丢失。
2. Modules：不要用 db / auto-script 这种不同抽象层级混着拆。按系统职责拆。
    - db 是物理的系统边界，auto-script 是我们这个MVP的应用层，不应该混在一起。
    - 模块儿目前我真的不会设计。
3. Domain/Data Model：这是这次重点。把系统中真正需要长期存在和管理的数据对象找出来，并说明关系。不要看到一个“动作”就建一个 Entity。
    数据的类型和建立
    - 用户数据
        raw | username, entropy-password
    - 检查记录
        raw | user_id, check_timestamp, service, url, status, response_time, result
    暂时我只能想到这些。
4. Health Check Flow：分别考虑 AUTO 和 MANUAL。注意 AUTO 没有操作用户。
    
    MANUL: user -> check -> result -> log -> record
    AUTO: system(占位符标识) | auto scripts -> check -> result -> log -> record

5. Authentication & Authorization：不能再写“上面说过”。我要看到需求如何被技术设计满足，尤其是 30min idle、8h absolute、disable/reset 后 session invalidation。
    登录后给30分钟token，8小时的cookie。
    30分钟后如果cookie失效，或者30分钟内没有任何操作，直接token -> blacklist；否则自动下发 refresh_token 但是需要用户自己做一次操作换取新的30分钟 access token，否则refresh token 10分钟失效。
    session 那部分我还是没有太懂，先不说了

6. Scheduler：如果你认为取决于生产环境，就写清楚你需要什么生产信息，以及不同环境为什么影响设计。
    单机部署和多node部署，实际上如果使用集群部署，和前面说的 redis + docker 就一样了

7. Technical Risks / Open Questions：鉴权现在已经从 open question 变成 confirmed requirement，所以你需要把它吸收到设计里；再判断现在还有什么风险。
    暂时想不出来了。
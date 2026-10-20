# tech leader 
你下一步先不要写代码，也不要建仓库。根据刚才确认的需求，给我提交一个简短的 Technical Design v0.1。
我希望至少看到：
1. 你准备使用什么技术栈，以及为什么。
    - python/fastapi 速度快，自动生成docs方便后续查阅测试
    - jwt + cookies 验证
    - docker redis 方便部署备份和并发

2. 系统准备拆成哪些主要模块。
    - user/role
    - check
    - auto-script
    - db 
3. 你认为有哪些核心数据对象，以及它们之间的关系。
    - user/role 所有action的基础
    - action/operation 动作： action 可以视为 user 针对账户的，operation 是为 user 使用系统功能的
    - response/result 动作触发的结果

4. Health Check 从触发到保存结果的大致数据流。
    - request -> 5s内 result -> response time -> 整合数据(用户、服务、时间、结果) -> db
5. 登录和权限准备怎么实现。
    - 上面说过了
6. 自动检查准备怎么调度。
    - 要根据生产环境看
7. 你认为目前最大的技术风险是什么
    - 万一有一些HTTP服务需要鉴权
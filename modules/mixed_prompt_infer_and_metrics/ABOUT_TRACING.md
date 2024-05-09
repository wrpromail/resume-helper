## 未解决的问题
在 langchain 的 chain 对象中，通过添加 callbacks 的方式添加 langsmith 的追踪。然后执行脚本2次，发现 langsmith 项目中 token 变化数目和 mistralai 官方控制台下模型 token 使用变化量不对齐。langsmith 中记录值明显小于官方记录值。


## langchain 在记录什么
（某一段时间内）llm调用次数、总计token、token消耗中位数、错误率、stream占比、p50 p99 延迟
（针对单次调用）链耗时（model调用耗时）、parser耗时（这项都为0）、运行环境信息（系统、版本）、CPU占用、上下文切换、请求占用的常驻内存、执行序列
是否将单次请求输入输出加入数据库
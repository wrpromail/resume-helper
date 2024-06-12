## deployment
#### plain usage by single docker container
```
# password at least should be 8 characters
docker run --name neo4j1 -p 7474:7474 -p 7687:7687 -d -e NEO4J_AUTH=neo4j/testtesttest neo4j:latest
```

## Graph Database Query Languages 
##### Cypher
Cypher 是 Neo4j 专有的图查询语言，专门设计用于声明性地对图数据库进行查询和更新操作。它的语法类似于 SQL，但更适合处理图数据结构，支持创建、读取、更新和删除节点和边。
###### commands
```
# 删除某个特定的 Person 节点及其所有关系：
MATCH (p:Person {name: 'Alice'}) DETACH DELETE p;
# 想清空整个数据库，可以使用以下查询：
MATCH (n) DETACH DELETE n;
```

##### GraphQL
GraphQL 是一种用于 API 查询的语言，由 Facebook 开发。它不是专门为图数据库设计的，但其查询模式和数据返回结构非常适合图形数据。GraphQL 可以用来查询各种数据源，包括图数据库。Neo4j 提供了 neo4j-graphql 库，可以将 GraphQL 查询直接映射到 Cypher 查询，实现无缝集成。
##### Gremlin
Gremlin 是 Apache TinkerPop 框架中的图遍历语言，设计用于在图数据库中进行遍历操作。与 Cypher 的声明性查询不同，Gremlin 更类似于编程语言，允许用户编写遍历图的逐步指令。Gremlin 可以与各种图数据库兼容，包括 Neo4j、Amazon Neptune 等。

## metrics(todo)
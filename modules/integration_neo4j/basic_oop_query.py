from basic_oop import Neo4jDatabase, Person, Department, Project

if __name__ == '__main__':
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "testtesttest"

    db = Neo4jDatabase(uri, username, password)
    # more data
    alice = Person(name="Alice", age=30, email="alice@example.com")
    bob = Person(name="Bob", age=25, email="bob@example.com")
    charlie = Person(name="Charlie", age=28, email="charlie@example.com")
    dave = Person(name="Dave", age=35, email="dave@example.com")

    engineering = Department(name="Engineering")
    marketing = Department(name="Marketing")

    project_x = Project(name="ProjectX", deadline="2024-12-31")
    project_y = Project(name="ProjectY", deadline="2025-06-30")

    db.create_nodes(alice, bob, charlie, dave, engineering, marketing, project_x, project_y)    
    
    relationships = [
        (alice, "BELONGS_TO", engineering),
        (bob, "BELONGS_TO", engineering),
        (charlie, "BELONGS_TO", marketing),
        (dave, "BELONGS_TO", engineering),

        (alice, "WORKS_ON", project_x),
        (bob, "WORKS_ON", project_x),
        (charlie, "WORKS_ON", project_y),
        (dave, "WORKS_ON", project_x)
    ]
    
    db.create_relationships(relationships)

    # 查询参与 x 项目的所有 eng 部门的人员
    query = """
    MATCH (p:Person)-[:BELONGS_TO]->(d:Department {name: 'Engineering'}),
          (p)-[:WORKS_ON]->(pr:Project {name: 'ProjectX'})
    RETURN p.name AS name, p.age AS age, p.email AS email
    """
    results = db.query(query)

    for record in results:
        print(f"Name: {record['name']}, Age: {record['age']}, Email: {record['email']}")

    db.close()

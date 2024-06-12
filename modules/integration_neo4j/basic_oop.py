from neo4j import GraphDatabase

class GraphObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def label(self):
        return self.__class__.__name__
    
    def properties(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

class Person(GraphObject):
    pass

class Department(GraphObject):
    pass

class Project(GraphObject):
    pass

class Neo4jDatabase:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_nodes(self, *objects):
        with self.driver.session() as session:
            for obj in objects:
                session.execute_write(self._create_node, obj)

    @staticmethod
    def _create_node(tx, obj):
        label = obj.label()
        properties = obj.properties()
        query = f"CREATE (n:{label} {{{', '.join([f'{k}: ${k}' for k in properties.keys()])}}})"
        tx.run(query, **properties)

    def create_relationships(self, relationships):
        with self.driver.session() as session:
            for start_node, rel_type, end_node in relationships:
                session.execute_write(self._create_relationship, start_node, rel_type, end_node)

    @staticmethod
    def _create_relationship(tx, start_node, rel_type, end_node):
        start_label = start_node.label()
        end_label = end_node.label()
        query = f"""
        MATCH (a:{start_label} {{name: $start_name}})
        MATCH (b:{end_label} {{name: $end_name}})
        CREATE (a)-[:{rel_type}]->(b)
        """
        tx.run(query, start_name=start_node.name, end_name=end_node.name)

    def query(self, query, **kwargs):
        with self.driver.session() as session:
            result = session.run(query, **kwargs)
            return [record for record in result]

# Usage example
if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "testtesttest"

    db = Neo4jDatabase(uri, username, password)

    # Create objects
    alice = Person(name="Alice", age=30, email="alice@example.com")
    bob = Person(name="Bob", age=25, email="bob@example.com")
    engineering = Department(name="Engineering")
    project_x = Project(name="ProjectX", deadline="2024-12-31")

    # Create nodes
    db.create_nodes(alice, bob, engineering, project_x)

    # Create relationships
    relationships = [
        (alice, "BELONGS_TO", engineering),
        (bob, "BELONGS_TO", engineering),
        (alice, "WORKS_ON", project_x),
        (bob, "WORKS_ON", project_x)
    ]

    db.create_relationships(relationships)

    db.close()
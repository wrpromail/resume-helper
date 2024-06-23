from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "testtesttest"

driver = GraphDatabase.driver(uri, auth=(username, password))

def create_person(tx, name):
    tx.run("CREATE (p:Person {name: $name})", name=name)

def create_friendship(tx, person1, person2):
    tx.run("""
    MATCH (p1:Person {name: $person1}), (p2:Person {name: $person2})
    CREATE (p1)-[:FRIEND]->(p2)
    """, person1=person1, person2=person2)

def find_friends(tx, name):
    result = tx.run("""
    MATCH (p:Person {name: $name})-[:FRIEND]->(friend)
    RETURN friend.name AS friend_name
    """, name=name)
    return [record["friend_name"] for record in result]

with driver.session() as session:
    session.execute_write(create_person, "Alice")
    session.execute_write(create_person, "Bob")
    session.execute_write(create_person, "Charlie")
    
    session.execute_write(create_friendship, "Alice", "Bob")
    session.execute_write(create_friendship, "Alice", "Charlie")
    
    friends_of_alice = session.execute_read(find_friends, "Alice")
    print(f"Alice's friends: {friends_of_alice}")

driver.close()
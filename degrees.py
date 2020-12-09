import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    # if len(sys.argv) > 2:
    #     sys.exit("Usage: python degrees.py [directory]")
    directory = "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    neighbors = list(neighbors_for_person(source))                                  
    stack = StackFrontier()
    path = []                                                              ## Once the targetId has been found, the result will be returned using this list
    explored = [source]

    for items in neighbors:                                                ## Checking the immediate neighbours of sourceId for targetId
        if(items[1] == target):                                            ## and returning the path if found
            stack.empty()                                                  ## or adding the neighbourId to stack.frontier if not found
            return [items]
        stack.add(Node(items[1], source, items[0]))
    
    for items in stack.frontier:                                           
        for co_actors in neighbors_for_person(items.state):                ## Calling the neigbours_for_person() on all ID's in stack.frontier
            
            if(co_actors[1] in explored):                                  ## skipping the neighbourId if it has already been explored
                continue

            explored.append(co_actors[1])                                  ## adding the neighbourId to explored list 

            if(co_actors[1] == target):                                    ## If the neighbourId is target, the path is generated and reuturned         
                tmp_node = Node(co_actors[1], items, co_actors[0])
                while True:
                    path.append((tmp_node.action, tmp_node.state))
                    tmp_node = tmp_node.parent
                    if(tmp_node == source):
                        stack.empty()
                        path.reverse()
                        return path
                    
            stack.add(Node(co_actors[1], items, co_actors[0]))            ## Else the neighbourId is added to the stack.frontier
    return None                                                     ## Once every single actor related to the source has been explored, None will be returned


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids=list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person=people[person_id]
            name=person["name"]
            birth=person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id=input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids=people[person_id]["movies"]
    neighbors=set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()

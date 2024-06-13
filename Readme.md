# DEVELOPMENT OF A LOCAL CHATBOT WITH A CUSTOMIZED KNOWLEDGE BASE

Bachelor Thesis on Bachelor's Degree in Computer Science

# Deployment
The deployment of the application simply consists on the execution of every component: LocalAI, Flask VectorDB, CouchDB and Website Application. In this repo you will find all the necessary files to build your own Docker containers. In some cases, a public DockerHub image is provided so that the user can pull it directly.

The environment has been adapted to work with CORS protocol, since in my situation I had to deploy the LocalAI part in a separated cluster computing node due to its high hardware specs demand, specially in terms of memory occupancy. This lets the user to also deploy the application in a personalized, distributed way.

There are some things to take into consideration, if the user wants to used the public DockerHub images. Since it is designed as to be deployed in a single machine (so when querying APIs the containers will search in localhost), and the ports are hardcoded, there are some considerations to take when running the docker containers:
- LocalAI should run on port 44444. 
- Flask vector database should run on port 5000.
- Website application defaults to port 8989.
- CouchDB defaults to 5984.

## Author

[Albert Cañadilla Domingo](https://github.com/acanadil/)
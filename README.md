# Local Tourist

![App Home Page](local_tourist/src/static/homePage.png)

## Project Overview
The "Local Tourist" project aims to provide users with personalized sorting of attractions, optimal routes for visiting attractions, and intuitive attraction ranking capabilities. For me, this project serves as a platform for gaining experience in working with cloud deployment, REST API connections, all things database, algorithms, Python, and the Flask framework.

## Tech Stack

- **Programming Language**: Local Tourist’s backend is coded in `Python` and frontend in `HTML/CSS`.
- **Web Framework**: The web framework is built using `Flask`, a lightweight web application framework.
- **Deployment Tools**: `Google Cloud` is used to deploy the website on Google App Engine
- **Libraries**: The `Google Maps API` library was used extensively for attraction indexing, map display, and route pathfinding
- **Version Control**: `Git` was employed for version control, allowing for efficient collaboration with team members.
- **Documentation Tools**: The codebase is well-commented to facilitate understanding and maintenance.

### Key Features
- Attraction searching based on geographical locations.
- Creation and modification of personalized plans for visiting attractions.
- Intuitive personal ranking list for attractions user has been to.
- Generation of optimal trip routes through the Google Maps API. <br>


## Roadmap
These features are planned implementations in future builds:
- Personalized sorting of attractions based on users similarity scores with other users
- Group creation and group trip planning
- AI NLP solution to suggest plans and attractions with automated feature engineering
- Robust testing framework

## Installation
This project is deployed via Google App Engine and can be accessed through this link:
<br> https://tourist-412606.uk.r.appspot.com
<br> Create an account to explore all of our features!


## Configuration
All configurations are managed through Google Cloud Platform (GCP).

## Usage
The project is web-based and communicates with multiple APIs, including the Google Maps API. An example usage scenario includes generating the optimal ordering of attractions to visit based on a user-specified list of places.

## Testing
Currently, there are no testing frameworks implemented in the project. They will be coming soon.

## Documentation
API documentation for integrating with Google Cloud Platform and the Google Maps API library can be found at:
<br> https://developers.google.com/maps
<br> https://cloud.google.com/docs

## Acknowledgments
Flask Quickstart application tutorial: This tutorial provided essential guidance for setting up basic page routes, database integration, and getting started with Flask application development. It served as a valuable resource for initiating the project's development process.

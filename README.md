# Steam Connect - A recommendation engine for Steam users
## Lawrence Chim


### Motivation
***

As part of my capstone project at Galvanize, I've created a recommender system
to connect Steam users based on similarities in gaming preference. As an avid
gamer myself, I would like to apply my knowledge of Data Science to a topic
that I greatly enjoy.

Valve currently does not a recommendation engine in place to for users to
connect with one another.

### Data
***

+ Collected information on 250,000 users, 12,500 games, and a total of
  15,941,228 ratings

+ Dimensionality Reduction: Removed games that saw an average playtime of less
  than 30 minutes across all users that own the game. The rationale for that
  is that games that have really low total playtime are probably not worth
  recommending. After filtering, I am left with 8484 games

+ Game specific information including:
    * Game Price
    * Detailed Description of Game
    * Release Date (MMM YYYY)
    * Metacritic rating
    * Game Genres
    * Top 5 community rated tags (if available)

### Modelling
***

+ As the utility matrix in question is sparse (~0.75% filled), a ranking matrix
  factorization with collaborative filtering were employed to predict ratings
  for unobserved data

+ Users were recommended based on the degree of cosine similarity it shares
  with one another

+ Two ratings model were created to help evaluate the performance of the
  recommender system:

    * Base rating model - ratings are directly proportional to the time the user
                          spent playing a particular game
    * Random rating model - ratings are randomly generated and the proportions
                            add up to 1

### Evaluation
***

+ To see if the base rating model performs better than random, a sample of 3,000
  users were selected to score the two models

+ Each of the two models generated a list of top 100 recommended users, and that
  list was compared with the actual friends the user has (Steam API has that
  function). The assumption here is that people who are friends share a degree of
  similarity in gaming preferences

+ As illustrated by the table below, the base rating model outperforms the
  random model quite significantly. Please note that there are over 125 million
  Steam users altogether, so the low score observed should not be surprising


  | Model                  |  Score (Max 3000) |
  | ---------------------- |  ----------------:|
  | Base Rating Model      |   59              |
  | Random Rating Model    |   41              |

### Future work
***

+ The current model could only recommend users that are trained. I would like to
  extend recommendations to new & unseen users

+ After matching two users, I would like to further suggest a multi-player game
  for them to play together

+ Build an interactive web app

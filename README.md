# Diglett 
A Pokémon which digs in repository documentation and detect _potentially_ outdated `README.md`. Diglett is a GitHub action and it checks:
 - When `README.md` was last modified.
 - Who did the last update and wheather the person is still member of the organization.  
 - Number of commits pushed since the `README.md` was last modified. 

Prints a short summary in the pull request review:
> ![diglett](https://raw.githubusercontent.com/TravelNest/diglett/master/diglett.gif)   
> Hello hello,  
> I am Diglett and I dig in your documentation! 
>
>:white_check_mark: :bust_in_silhouette: **GitHubUser** last modified the `README.md`, who is still member of GitHub org.  
:white_check_mark: :date: `README.md` was last modified: 2019-04-14T19:55:36Z   
:white_check_mark: :hash: Since then **5 commits** were pushed   
>
>:memo: Update your `README.md` and keep the repo up to dated!


## Usage
Add `digglet.yml` into your `.github/worflow` directory in root of your github repo. Then on each pull request Diglett will check
your repo documentation and post a comment in your PR review.
```yaml
on: pull_request

jobs:
  digglet:
    runs-on: ubuntu-latest
    name: Diglett
    steps:
    - name: Diglett documentation check
      id: diglett
      uses: TravelNest/diglett@master
      with:
        TOKEN: ${{ secrets.GITHUB_TOKEN }}
        PR_NUMBER: ${{ github.event.pull_request.number }}
        MAX_COMMITS: 100
        MAX_DAYS: 50
    - name: Diglett result
      run: echo ${{ steps.diglett.outputs.OutputMessage }} 
```

## TODO:
 - [ ] add tests
 - [x] search for all README.md in repo
 - [ ] search for TODOs in code
 - [ ] add makefile with tests & lint


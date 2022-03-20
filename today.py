import datetime
from dateutil import relativedelta
import requests
import os
from xml.dom import minidom

try: # This should run locally
    import config
    ACCESS_TOKEN = config.ACCESS_TOKEN
    OWNER_ID = config.OWNER_ID
    USER_NAME = config.USER_NAME

except: # This should run on GitHub Actions
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
    OWNER_ID = os.environ['OWNER_ID']
    USER_NAME = os.environ['USER_NAME']

HEADERS = {'authorization': 'token '+ ACCESS_TOKEN}


def daily_readme():
    """
    Returns the length of time since I was born
    e.g. 'XX years, XX months, XX days'
    """
    birth = datetime.datetime(2002, 7, 5)
    diff = relativedelta.relativedelta(datetime.datetime.today(), birth)
    return '{} {}, {} {}, {} {}'.format(
        diff.years, 'year' + format_plural(diff.years), 
        diff.months, 'month' + format_plural(diff.months), 
        diff.days, 'day' + format_plural(diff.days)
        )


def format_plural(unit):
    """
    Returns a properly formatted number
    e.g.
    'day' + format_plural(diff.days) == 5
    >>> '5 days'
    'day' + format_plural(diff.days) == 1
    >>> '1 day'
    """
    if unit != 1: return 's'
    return ''


def graph_commits(start_date, end_date):
    """
    Uses GitHub's GraphQL v4 API to return my total commit count
    """
    query = '''
    query($start_date: DateTime!, $end_date: DateTime!, $login: String!) {
        user(login: $login) {
            contributionsCollection(from: $start_date, to: $end_date) {
                contributionCalendar {
                    totalContributions
                }
            }
        }
    }'''
    variables = {'start_date': start_date,'end_date': end_date, 'login': USER_NAME}
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables':variables}, headers=HEADERS)
    if request.status_code == 200:
        return int(request.json()['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions'])
    raise Exception("the request has failed, graph_commits()")


def graph_repos_stars_loc(count_type, owner_affiliation):
    """
    Uses GitHub's GraphQL v4 API to return my total repository, star, or lines of code count.
    This is a separate function from graph_commits, because graph_commits queries -(-x // 100) times (where x is my total commit count),
    and this runs once (per call, and it is called thrice)
    """
    query = '''
    query ($owner_affiliation: [RepositoryAffiliation], $login: String!) {
        user(login: $login) {
            repositories(first: 100, ownerAffiliations: $owner_affiliation) {
                totalCount
                edges {
                    node {
                        ... on Repository {
                            nameWithOwner
                            stargazers {
                                totalCount
                            }
                            owner {
                                id
                            }
                        }
                    }
                }
            }
        }
    }'''
    variables = {'owner_affiliation': owner_affiliation, 'login': USER_NAME}
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables':variables}, headers=HEADERS)
    if request.status_code == 200:
        if count_type == "repos":
            return request.json()['data']['user']['repositories']['totalCount']
        elif count_type == "stars":
            return stars_counter(request.json()['data']['user']['repositories']['edges'])
        else:
            return all_repo_names(request.json()['data']['user']['repositories']['edges'])
    raise Exception("the request has failed, graph_repos_stars()")


def all_repo_names(data):
    """
    Returns the total number of lines of code written by my account
    """
    add_loc, del_loc = 0, 0
    for node in data:
        name_with_owner = node['node']['nameWithOwner'].split('/')
        repo_name = name_with_owner[1]
        owner = name_with_owner[0]
        add_loc += query_loc(owner, repo_name)[0]
        del_loc += query_loc(owner, repo_name)[1]
    total_loc = add_loc - del_loc
    return [add_loc, del_loc, total_loc]


def query_loc(owner, repo_name, addition_total=0, deletion_total=0, cursor=None):
    """
    Uses GitHub's GraphQL v4 API to fetch 100 commits at a time
    This is a separate function from graph_commits and graph_repos_stars_loc, because this is called hundreds of times
    """
    query = '''
    query ($repo_name: String!, $owner: String!, $cursor: String) {
        repository(name: $repo_name, owner: $owner) {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(first: 100, after: $cursor) {
                            totalCount
                            edges {
                                node {
                                    ... on Commit {
                                        committedDate
                                    }
                                    author {
                                        user {
                                            id
                                        }
                                    }
                                    deletions
                                    additions
                                }
                                cursor
                            }
                        }
                    }
                }
            }
        }
    }'''
    variables = {"repo_name": repo_name, "owner": owner, "cursor": cursor}
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables':variables}, headers=HEADERS)
    if request.status_code == 200:
        if request.json()['data']['repository']['defaultBranchRef'] != None: # Only count commits if repo isn't empty
            return loc_counter_one_repo(owner, repo_name, request.json()['data']['repository']['defaultBranchRef']['target']['history']['edges'], addition_total, deletion_total, cursor)
        else:
            return 0
    else:
        raise Exception("the request has failed, query_loc()")


def loc_counter_one_repo(owner, repo_name, edges, addition_total, deletion_total, cursor=None, new_cursor="0"):
    """
    Recursively call query_loc (since GraphQL can only search 100 commits at a time) 
    only adds the LOC value of commits authored by me
    """
    if edges == []: # beginning of commit history
        return addition_total, deletion_total
    for node in edges:
        new_cursor = node['cursor'] # redefine cursor over and over again until it reaches the last node in the call
        if node['node']['author']['user'] == {'id': OWNER_ID}:
            addition_total += node['node']['additions']
            deletion_total += node['node']['deletions']
    return query_loc(owner, repo_name, addition_total, deletion_total, new_cursor)


def stars_counter(data):
    """
    Count total stars in repositories owned by me
    """
    total_stars = 0
    for node in data:
        total_stars += node['node']['stargazers']['totalCount']
    return total_stars


def svg_overwrite(filename, age_data, commit_data, star_data, repo_data, loc_data):
    """
    Parse SVG files and update elements with my age, commits, stars, repositories, and lines written
    """
    svg = minidom.parse(filename)
    f = open(filename, mode='w', encoding='utf-8')
    tspan = svg.getElementsByTagName('tspan')
    tspan[30].firstChild.data = age_data
    tspan[65].firstChild.data = repo_data
    tspan[67].firstChild.data = commit_data
    tspan[69].firstChild.data = star_data
    tspan[71].firstChild.data = loc_data[2]
    tspan[72].firstChild.data = loc_data[0] + "++"
    tspan[73].firstChild.data = loc_data[1] + "--"
    f.write(svg.toxml("utf-8").decode("utf-8"))


def commit_counter(date):
    """
    Counts up my total commits.
    Loops commits per year (starting backwards from today, continuing until my account's creation date)
    """
    total_commits = 0
    # since GraphQL's contributionsCollection has a maximum reach of one year
    while date.isoformat() > "2019-11-02T00:00:00.000Z": # one day before my very first commit
        old_date = date.isoformat()
        date = date - datetime.timedelta(days=365)
        total_commits += graph_commits(date.isoformat(), old_date)
    return total_commits


def svg_element_getter(filename):
    """
    Prints the element index of every element in the SVG file
    """
    svg = minidom.parse(filename)
    open(filename, mode='r', encoding='utf-8')
    tspan = svg.getElementsByTagName('tspan')
    for index in range(len(tspan)): print(index, tspan[index].firstChild.data)

if __name__ == '__main__':
    """
    Runs program over each SVG image
    """
    age_data = daily_readme()
    # f' for whitespace, "{;,}" for commas
    commit_data = f'{"{:,}".format(commit_counter(datetime.datetime.today())): <7}'
    star_data = "{:,}".format(graph_repos_stars_loc("stars", ["OWNER"]))
    repo_data = f'{"{:,}".format(graph_repos_stars_loc("repos", ["OWNER"])): <6}'
    total_loc = graph_repos_stars_loc("LOC", ["OWNER", "COLLABORATOR", "ORGANIZATION_MEMBER"])
    
    for index in range(len(total_loc)): total_loc[index] = "{:,}".format(total_loc[index]) # format added, deleted, and total LOC

    svg_overwrite("dark_mode.svg", age_data, commit_data, star_data, repo_data, total_loc)
    svg_overwrite("light_mode.svg", age_data, commit_data, star_data, repo_data, total_loc)
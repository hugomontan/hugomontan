import os
import requests
from lxml import etree

# Variáveis de ambiente para o token e nome de usuário
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')  # A variável de ambiente fornecida pelo GitHub Actions
USER_NAME = os.getenv('USER_NAME')  # A variável de ambiente fornecida pelo GitHub Actions

HEADERS = {'Authorization': f'token {ACCESS_TOKEN}'}

def fetch_github_metrics():
    """
    Função para buscar as métricas do GitHub usando a API GraphQL.
    Retorna um dicionário com as métricas: repos, stars, commits, followers, loc.
    """
    query = '''
    query($login: String!) {
        user(login: $login) {
            repositories {
                totalCount
            }
            stargazers {
                totalCount
            }
            contributionsCollection {
                contributionCalendar {
                    totalContributions
                }
            }
            followers {
                totalCount
            }
            repositoriesContributedTo {
                totalCount
            }
            repositories {
                edges {
                    node {
                        nameWithOwner
                        defaultBranchRef {
                            target {
                                ... on Commit {
                                    history {
                                        totalCount
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }'''

    variables = {'login': USER_NAME}
    
    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': query, 'variables': variables},
        headers=HEADERS
    )
    
    if response.status_code != 200:
        raise Exception(f"Error fetching GitHub data: {response.status_code}")
    
    data = response.json()
    user_data = data['data']['user']

    # Calculando métricas
    repos_count = user_data['repositories']['totalCount']
    stars_count = user_data['stargazers']['totalCount']
    commits_count = user_data['contributionsCollection']['contributionCalendar']['totalContributions']
    followers_count = user_data['followers']['totalCount']
    
    # LINHAS DE CÓDIGO - Precisamos de um extra query para contar as LOC
    loc_count = sum(
        repo['node']['defaultBranchRef']['target']['history']['totalCount']
        for repo in user_data['repositories']['edges']
    )
    
    return {
        'repos': repos_count,
        'stars': stars_count,
        'commits': commits_count,
        'followers': followers_count,
        'loc': loc_count
    }

def update_svg(metrics):
    """
    Atualiza o arquivo SVG com as novas métricas do GitHub.
    """
    # Carregar o SVG original
    tree = etree.parse('profile_template.svg')
    root = tree.getroot()

    # Atualizar as métricas no SVG
    find_and_replace(root, 'repo_data', str(metrics['repos']))
    find_and_replace(root, 'star_data', str(metrics['stars']))
    find_and_replace(root, 'commit_data', str(metrics['commits']))
    find_and_replace(root, 'follower_data', str(metrics['followers']))
    find_and_replace(root, 'loc_data', str(metrics['loc']))

    # Salvar o SVG atualizado
    tree.write('updated_profile.svg', encoding='utf-8', xml_declaration=True)

def find_and_replace(root, element_id, new_text):
    """
    Função para encontrar e substituir texto de um elemento SVG pelo ID.
    """
    element = root.find(f".//*[@id='{element_id}']")
    if element is not None:
        element.text = new_text

if __name__ == '__main__':
    # Buscar as métricas do GitHub
    metrics = fetch_github_metrics()

    # Atualizar o SVG com as novas métricas
    update_svg(metrics)

    print("SVG atualizado com as novas métricas do GitHub!")

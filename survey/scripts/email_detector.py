import os

import requests
from typing import List, Dict
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TOKEN    = os.getenv('API_TOKEN')


class GitHubEmailCollector:
    def __init__(self, token: str):
        """
        Inicializa o coletor de emails
        :param token: Token de acesso pessoal do GitHub
        """
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'

    def get_contributors(self, repo_full_name: str) -> List[Dict]:
        """
        Obtém a lista de contribuidores de um repositório
        :param repo_full_name: Nome completo do repositório (formato: 'dono/repositório')
        :return: Lista de contribuidores
        """
        url = f"{self.base_url}/repos/{repo_full_name}/contributors"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao obter contribuidores para {repo_full_name}: {response.status_code}")
            return []

    def get_user_email(self, username: str) -> str:
        """
        Obtém o email público do usuário
        :param username: Nome de usuário do GitHub
        :return: Email do usuário ou None se não encontrado
        """
        url = f"{self.base_url}/users/{username}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            user_data = response.json()
            return user_data.get('email')
        return None

    def get_commit_emails(self, repo_full_name: str, username: str) -> List[str]:
        """
        Obtém emails dos commits do usuário
        :param repo_full_name: Nome completo do repositório
        :param username: Nome de usuário do GitHub
        :return: Lista de emails encontrados
        """
        url = f"{self.base_url}/repos/{repo_full_name}/commits"
        params = {'author': username}
        response = requests.get(url, headers=self.headers, params=params)

        emails = set()
        if response.status_code == 200:
            commits = response.json()
            for commit in commits:
                if commit.get('commit', {}).get('author', {}).get('email'):
                    emails.add(commit['commit']['author']['email'])
        return list(emails)


def process_repositories(repos: List[str], github_token: str) -> List[Dict]:
    """
    Processa uma lista de repositórios e coleta emails dos contribuidores
    :param repos: Lista de repositórios no formato 'dono/repositório'
    :param github_token: Token de acesso pessoal do GitHub
    :return: Lista de dicionários com informações de repositório, usuário e emails
    """
    collector = GitHubEmailCollector(github_token)
    results = []

    for repo in repos:
        print(f"Processando repositório: {repo}")
        contributors = collector.get_contributors(repo)

        for contributor in contributors:
            username = contributor['login']
            emails = set()

            # Try to get a public email
            email = collector.get_user_email(username)
            if email:
                emails.add(email)

            # Tenta obter emails dos commits
            commit_emails = collector.get_commit_emails(repo, username)
            emails.update(commit_emails)

            emails_list = list(emails)
            result = {
                'repository': repo,
                'username': username,
                'email1': emails_list[0] if len(emails_list) > 0 else '',
                'email2': emails_list[1] if len(emails_list) > 1 else '',
                'email3': emails_list[2] if len(emails_list) > 2 else '',
                'email4': emails_list[3] if len(emails_list) > 3 else ''

            }
            results.append(result)

    return results


# Exemplo de uso
if __name__ == "__main__":
    repositories = pd.read_csv('../../data_collection/dataset/_processed_data-[experiment_used]/[ENGLISH-DESC]_repo-files_2025-11-12_15:09:21.csv', usecols=['full_name'])['full_name'].tolist()
    # print(repositories)

    # Collect the emails
    results = process_repositories(repositories, TOKEN)

    # Save results in a CSV file
    df = pd.DataFrame(results)
    df.to_csv('[Github_Emails]-ENGLISH-DESC.csv', index=False)

    # Imprime os resultados
    print("\nData saved")

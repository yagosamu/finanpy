"""
Test script to verify authentication protection on Django routes.
Tests that protected routes redirect unauthenticated users to login page.
"""
import requests
from urllib.parse import urlparse, parse_qs

# Base URL for the Django development server
BASE_URL = 'http://localhost:8000'

# Routes that should be protected (require authentication)
PROTECTED_ROUTES = [
    '/dashboard/',
    '/perfil/',
    '/perfil/editar/',
]

# Expected login URL
EXPECTED_LOGIN_PATH = '/usuarios/login/'


def test_route_protection(route):
    """
    Test a single protected route.

    Args:
        route: The route path to test

    Returns:
        dict: Test results containing status, redirect_url, and other info
    """
    # Create a new session (clean, no cookies)
    session = requests.Session()

    # Make GET request to the protected route
    url = f'{BASE_URL}{route}'

    try:
        # Allow redirects and capture the final URL
        response = session.get(url, allow_redirects=True)

        # Parse the final URL after all redirects
        final_url = response.url
        parsed_url = urlparse(final_url)
        final_path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        # Check if redirected to login page
        redirected_to_login = final_path == EXPECTED_LOGIN_PATH

        # Check if 'next' parameter exists and points to original route
        has_next_param = 'next' in query_params
        next_param_value = query_params.get('next', [''])[0] if has_next_param else None
        next_param_correct = next_param_value == route if has_next_param else False

        # Determine if test passed
        test_passed = redirected_to_login and has_next_param and next_param_correct

        return {
            'route': route,
            'status': 'PASSOU' if test_passed else 'FALHOU',
            'initial_url': url,
            'final_url': final_url,
            'final_path': final_path,
            'redirected_to_login': redirected_to_login,
            'has_next_param': has_next_param,
            'next_param_value': next_param_value,
            'next_param_correct': next_param_correct,
            'status_code': response.status_code,
        }

    except Exception as e:
        return {
            'route': route,
            'status': 'ERRO',
            'error': str(e),
        }


def test_login_page_accessible():
    """Test that the login page is accessible without authentication."""
    session = requests.Session()
    url = f'{BASE_URL}{EXPECTED_LOGIN_PATH}'

    try:
        response = session.get(url, allow_redirects=True)

        return {
            'route': EXPECTED_LOGIN_PATH,
            'status': 'PASSOU' if response.status_code == 200 else 'FALHOU',
            'status_code': response.status_code,
            'accessible': response.status_code == 200,
            'contains_form': 'email' in response.text.lower() and 'senha' in response.text.lower(),
        }

    except Exception as e:
        return {
            'route': EXPECTED_LOGIN_PATH,
            'status': 'ERRO',
            'error': str(e),
        }


def main():
    """Run all authentication protection tests."""
    print('='*80)
    print('TESTE DE PROTECAO DE ROTAS AUTENTICADAS')
    print('='*80)
    print()

    results = []

    # Test each protected route
    print('Testando rotas protegidas...')
    print('-'*80)
    for route in PROTECTED_ROUTES:
        print(f'Testando: {route}')
        result = test_route_protection(route)
        results.append(result)

        print(f'  Status: {result["status"]}')
        if result['status'] != 'ERRO':
            print(f'  URL Final: {result["final_url"]}')
            print(f'  Redirecionado para login: {result["redirected_to_login"]}')
            print(f'  Parametro "next" presente: {result["has_next_param"]}')
            print(f'  Valor do "next": {result["next_param_value"]}')
            print(f'  Parametro "next" correto: {result["next_param_correct"]}')
        else:
            print(f'  Erro: {result["error"]}')
        print()

    # Test login page accessibility
    print('Testando acessibilidade da pagina de login...')
    print('-'*80)
    login_result = test_login_page_accessible()
    print(f'Rota: {login_result["route"]}')
    print(f'Status: {login_result["status"]}')
    if login_result['status'] != 'ERRO':
        print(f'Status Code: {login_result["status_code"]}')
        print(f'Acessivel: {login_result["accessible"]}')
        print(f'Contem formulario de login: {login_result["contains_form"]}')
    else:
        print(f'Erro: {login_result["error"]}')
    print()

    # Summary
    print('='*80)
    print('RESUMO')
    print('='*80)
    passed = sum(1 for r in results if r['status'] == 'PASSOU')
    failed = sum(1 for r in results if r['status'] == 'FALHOU')
    errors = sum(1 for r in results if r['status'] == 'ERRO')

    print(f'Total de testes: {len(results)}')
    print(f'Passou: {passed}')
    print(f'Falhou: {failed}')
    print(f'Erros: {errors}')
    print()

    if failed > 0 or errors > 0:
        print('FALHAS DETECTADAS:')
        for result in results:
            if result['status'] in ['FALHOU', 'ERRO']:
                print(f'  - {result["route"]}: {result["status"]}')
                if 'error' in result:
                    print(f'    Erro: {result["error"]}')
                elif not result.get('redirected_to_login', False):
                    print(f'    Razao: Nao redirecionou para {EXPECTED_LOGIN_PATH}')
                elif not result.get('has_next_param', False):
                    print(f'    Razao: Parametro "next" nao encontrado na URL')
                elif not result.get('next_param_correct', False):
                    print(f'    Razao: Parametro "next" incorreto')
    else:
        print('TODOS OS TESTES PASSARAM!')

    print('='*80)

    return results, login_result


if __name__ == '__main__':
    main()

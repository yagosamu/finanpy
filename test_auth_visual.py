"""
Visual evidence generator for authentication protection tests.
Creates detailed console output with visual formatting.
"""
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime


def print_header(text):
    """Print a formatted header."""
    width = 80
    print('\n' + '='*width)
    print(text.center(width))
    print('='*width + '\n')


def print_section(text):
    """Print a formatted section."""
    width = 80
    print('\n' + '-'*width)
    print(text)
    print('-'*width)


def print_result(label, value, passed=None):
    """Print a test result with visual indicator."""
    if passed is None:
        print(f'  {label:.<50} {value}')
    elif passed:
        print(f'  {label:.<50} {value} [OK]')
    else:
        print(f'  {label:.<50} {value} [FALHA]')


def test_protected_route(route, route_name):
    """Test a protected route and print visual results."""
    print_section(f'Testando: {route_name} ({route})')

    session = requests.Session()
    url = f'http://localhost:8000{route}'

    try:
        response = session.get(url, allow_redirects=True)

        final_url = response.url
        parsed_url = urlparse(final_url)
        final_path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        redirected_to_login = final_path == '/usuarios/login/'
        has_next_param = 'next' in query_params
        next_param_value = query_params.get('next', [''])[0] if has_next_param else None
        next_param_correct = next_param_value == route if has_next_param else False

        print('\n1. URL INICIAL:')
        print_result('URL', url)

        print('\n2. COMPORTAMENTO DE REDIRECT:')
        print_result('Numero de redirects', len(response.history))
        print_result('URL Final', final_url)

        print('\n3. VERIFICACOES DE SEGURANCA:')
        print_result('Redirecionou para /usuarios/login/',
                    'SIM' if redirected_to_login else 'NAO',
                    redirected_to_login)
        print_result('Parametro "next" presente',
                    'SIM' if has_next_param else 'NAO',
                    has_next_param)
        print_result('Valor do parametro "next"',
                    f'"{next_param_value}"' if next_param_value else 'N/A')
        print_result('Parametro "next" correto',
                    'SIM' if next_param_correct else 'NAO',
                    next_param_correct)

        print('\n4. RESPOSTA HTTP:')
        print_result('Status Code', response.status_code)
        print_result('Content-Type', response.headers.get('Content-Type', 'N/A'))

        # Check login form elements
        html = response.text.lower()
        has_email = 'email' in html and ('type="email"' in html or 'name="email"' in html)
        has_password = 'type="password"' in html
        has_csrf = 'csrfmiddlewaretoken' in html

        print('\n5. CONTEUDO DA PAGINA DE LOGIN:')
        print_result('Campo de email presente',
                    'SIM' if has_email else 'NAO',
                    has_email)
        print_result('Campo de senha presente',
                    'SIM' if has_password else 'NAO',
                    has_password)
        print_result('Token CSRF presente',
                    'SIM' if has_csrf else 'NAO',
                    has_csrf)

        # Overall result
        all_passed = (redirected_to_login and has_next_param and
                     next_param_correct and has_email and has_password and has_csrf)

        print('\n6. RESULTADO FINAL:')
        if all_passed:
            print_result('Status do Teste', 'PASSOU', True)
            print('\n  A rota esta CORRETAMENTE PROTEGIDA!')
            print('  - Usuarios nao autenticados sao redirecionados para o login')
            print('  - O parametro "next" preserva a URL original')
            print('  - A pagina de login possui todos os elementos necessarios')
        else:
            print_result('Status do Teste', 'FALHOU', False)
            print('\n  ATENCAO: Problemas detectados na protecao da rota!')

        return all_passed

    except Exception as e:
        print(f'\n  ERRO: {str(e)}')
        return False


def test_login_page_direct():
    """Test direct access to login page."""
    print_section('Testando: Acesso Direto a Pagina de Login')

    session = requests.Session()
    url = 'http://localhost:8000/usuarios/login/'

    try:
        response = session.get(url, allow_redirects=True)

        print('\n1. URL ACESSADA:')
        print_result('URL', url)

        print('\n2. RESPOSTA:')
        print_result('Status Code', response.status_code)
        print_result('Acessivel',
                    'SIM' if response.status_code == 200 else 'NAO',
                    response.status_code == 200)

        # Check form elements
        html = response.text.lower()
        has_email = 'email' in html and ('type="email"' in html or 'name="email"' in html)
        has_password = 'type="password"' in html
        has_submit = '<button' in html or 'type="submit"' in html
        has_csrf = 'csrfmiddlewaretoken' in html

        print('\n3. ELEMENTOS DO FORMULARIO:')
        print_result('Campo de email',
                    'Presente' if has_email else 'Ausente',
                    has_email)
        print_result('Campo de senha',
                    'Presente' if has_password else 'Ausente',
                    has_password)
        print_result('Botao de submit',
                    'Presente' if has_submit else 'Ausente',
                    has_submit)
        print_result('Token CSRF',
                    'Presente' if has_csrf else 'Ausente',
                    has_csrf)

        all_passed = (response.status_code == 200 and has_email and
                     has_password and has_submit and has_csrf)

        print('\n4. RESULTADO:')
        if all_passed:
            print_result('Status do Teste', 'PASSOU', True)
            print('\n  A pagina de login esta FUNCIONANDO CORRETAMENTE!')
        else:
            print_result('Status do Teste', 'FALHOU', False)

        return all_passed

    except Exception as e:
        print(f'\n  ERRO: {str(e)}')
        return False


def main():
    """Run visual authentication tests."""
    print_header('TESTE DE PROTECAO DE ROTAS AUTENTICADAS - FINANPY')

    print(f'Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    print(f'Servidor: http://localhost:8000')
    print(f'Metodo: Requisicoes HTTP com sessao limpa (sem cookies)')

    # Test protected routes
    routes = [
        ('/dashboard/', 'Dashboard'),
        ('/perfil/', 'Perfil do Usuario'),
        ('/perfil/editar/', 'Edicao de Perfil'),
    ]

    results = []
    for route, name in routes:
        result = test_protected_route(route, name)
        results.append((name, result))

    # Test login page
    login_result = test_login_page_direct()

    # Final summary
    print_header('RESUMO FINAL')

    print('ROTAS PROTEGIDAS TESTADAS:\n')
    for name, passed in results:
        status = 'PASSOU' if passed else 'FALHOU'
        symbol = 'OK' if passed else 'FALHA'
        print(f'  [{symbol}] {name:.<50} {status}')

    print(f'\n  [{"OK" if login_result else "FALHA"}] {"Pagina de Login":.<50} {"PASSOU" if login_result else "FALHOU"}')

    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    failed_count = total - passed_count

    print(f'\n\nESTATISTICAS:')
    print(f'  Total de rotas testadas: {total}')
    print(f'  Passou: {passed_count}')
    print(f'  Falhou: {failed_count}')

    if failed_count == 0 and login_result:
        print('\n' + '='*80)
        print('TODOS OS TESTES PASSARAM!'.center(80))
        print('O sistema esta corretamente protegido contra acesso nao autorizado.'.center(80))
        print('='*80)
    else:
        print('\n' + '='*80)
        print('FALHAS DETECTADAS!'.center(80))
        print('Algumas rotas podem estar vulneraveis.'.center(80))
        print('='*80)


if __name__ == '__main__':
    main()

"""
Enhanced test script with detailed reporting for authentication protection.
Generates a comprehensive markdown report with evidence.
"""
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import re

# Base URL for the Django development server
BASE_URL = 'http://localhost:8000'

# Routes that should be protected (require authentication)
PROTECTED_ROUTES = [
    {'path': '/dashboard/', 'name': 'Dashboard'},
    {'path': '/perfil/', 'name': 'Perfil do Usuario'},
    {'path': '/perfil/editar/', 'name': 'Edicao de Perfil'},
]

# Expected login URL
EXPECTED_LOGIN_PATH = '/usuarios/login/'


def analyze_html_content(html):
    """Analyze HTML content to extract relevant information."""
    info = {
        'has_email_field': bool(re.search(r'(type=["\']email["\']|name=["\']email["\']|id=["\']id_email["\'])', html, re.IGNORECASE)),
        'has_password_field': bool(re.search(r'(type=["\']password["\']|name=["\']password["\'])', html, re.IGNORECASE)),
        'has_submit_button': bool(re.search(r'(type=["\']submit["\']|<button)', html, re.IGNORECASE)),
        'has_csrf_token': bool(re.search(r'csrfmiddlewaretoken', html, re.IGNORECASE)),
        'title': '',
    }

    # Try to extract page title
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    if title_match:
        info['title'] = title_match.group(1).strip()

    return info


def test_route_protection(route_info):
    """Test a single protected route with detailed analysis."""
    route = route_info['path']
    session = requests.Session()
    url = f'{BASE_URL}{route}'

    try:
        response = session.get(url, allow_redirects=True)

        final_url = response.url
        parsed_url = urlparse(final_url)
        final_path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        redirected_to_login = final_path == EXPECTED_LOGIN_PATH
        has_next_param = 'next' in query_params
        next_param_value = query_params.get('next', [''])[0] if has_next_param else None
        next_param_correct = next_param_value == route if has_next_param else False

        # Analyze HTML content if redirected to login
        html_analysis = None
        if redirected_to_login:
            html_analysis = analyze_html_content(response.text)

        test_passed = redirected_to_login and has_next_param and next_param_correct

        return {
            'route': route,
            'route_name': route_info['name'],
            'status': 'PASSOU' if test_passed else 'FALHOU',
            'initial_url': url,
            'final_url': final_url,
            'final_path': final_path,
            'redirected_to_login': redirected_to_login,
            'has_next_param': has_next_param,
            'next_param_value': next_param_value,
            'next_param_correct': next_param_correct,
            'status_code': response.status_code,
            'html_analysis': html_analysis,
            'redirect_count': len(response.history),
        }

    except Exception as e:
        return {
            'route': route,
            'route_name': route_info['name'],
            'status': 'ERRO',
            'error': str(e),
        }


def test_login_page():
    """Test login page with detailed analysis."""
    session = requests.Session()
    url = f'{BASE_URL}{EXPECTED_LOGIN_PATH}'

    try:
        response = session.get(url, allow_redirects=True)
        html_analysis = analyze_html_content(response.text)

        return {
            'route': EXPECTED_LOGIN_PATH,
            'status': 'PASSOU' if response.status_code == 200 else 'FALHOU',
            'status_code': response.status_code,
            'accessible': response.status_code == 200,
            'html_analysis': html_analysis,
        }

    except Exception as e:
        return {
            'route': EXPECTED_LOGIN_PATH,
            'status': 'ERRO',
            'error': str(e),
        }


def generate_markdown_report(results, login_result):
    """Generate a detailed markdown report."""
    report = []
    report.append('# Relatorio de Teste de Protecao de Rotas Autenticadas\n')
    report.append(f'**Data:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')
    report.append(f'**URL Base:** {BASE_URL}\n')
    report.append(f'**URL de Login Esperada:** {EXPECTED_LOGIN_PATH}\n')
    report.append('\n---\n\n')

    # Overall summary
    passed = sum(1 for r in results if r['status'] == 'PASSOU')
    failed = sum(1 for r in results if r['status'] == 'FALHOU')
    errors = sum(1 for r in results if r['status'] == 'ERRO')

    report.append('## Resumo Geral\n\n')
    report.append(f'- **Total de Rotas Testadas:** {len(results)}\n')
    report.append(f'- **Passou:** {passed}\n')
    report.append(f'- **Falhou:** {failed}\n')
    report.append(f'- **Erros:** {errors}\n')

    if failed == 0 and errors == 0:
        report.append('\n**Status:** TODOS OS TESTES PASSARAM ✓\n')
    else:
        report.append('\n**Status:** FALHAS DETECTADAS ✗\n')

    report.append('\n---\n\n')

    # Detailed results for each route
    report.append('## Resultados Detalhados por Rota\n\n')

    for result in results:
        report.append(f'### {result["route_name"]} (`{result["route"]}`)\n\n')
        report.append(f'**Status:** {result["status"]}\n\n')

        if result['status'] == 'ERRO':
            report.append(f'**Erro:** {result["error"]}\n\n')
            continue

        report.append('#### Verificacoes\n\n')
        report.append('| Verificacao | Resultado |\n')
        report.append('|-------------|----------|\n')
        report.append(f'| Redirecionou para login | {"✓ Sim" if result["redirected_to_login"] else "✗ Nao"} |\n')
        report.append(f'| Parametro "next" presente | {"✓ Sim" if result["has_next_param"] else "✗ Nao"} |\n')
        report.append(f'| Parametro "next" correto | {"✓ Sim" if result["next_param_correct"] else "✗ Nao"} |\n')
        report.append(f'| Status Code | {result["status_code"]} |\n')
        report.append(f'| Numero de Redirects | {result["redirect_count"]} |\n')
        report.append('\n')

        report.append('#### URLs\n\n')
        report.append(f'- **URL Inicial:** `{result["initial_url"]}`\n')
        report.append(f'- **URL Final:** `{result["final_url"]}`\n')
        report.append(f'- **Path Final:** `{result["final_path"]}`\n')
        if result.get('next_param_value'):
            report.append(f'- **Valor do Parametro "next":** `{result["next_param_value"]}`\n')
        report.append('\n')

        if result.get('html_analysis'):
            report.append('#### Analise da Pagina de Login\n\n')
            analysis = result['html_analysis']
            report.append(f'- **Campo de Email:** {"✓ Presente" if analysis["has_email_field"] else "✗ Ausente"}\n')
            report.append(f'- **Campo de Senha:** {"✓ Presente" if analysis["has_password_field"] else "✗ Ausente"}\n')
            report.append(f'- **Botao de Submit:** {"✓ Presente" if analysis["has_submit_button"] else "✗ Ausente"}\n')
            report.append(f'- **Token CSRF:** {"✓ Presente" if analysis["has_csrf_token"] else "✗ Ausente"}\n')
            if analysis.get('title'):
                report.append(f'- **Titulo da Pagina:** {analysis["title"]}\n')
            report.append('\n')

        report.append('---\n\n')

    # Login page test
    report.append('## Teste da Pagina de Login\n\n')
    report.append(f'**Rota:** `{login_result["route"]}`\n\n')
    report.append(f'**Status:** {login_result["status"]}\n\n')

    if login_result['status'] != 'ERRO':
        report.append('#### Verificacoes\n\n')
        report.append('| Verificacao | Resultado |\n')
        report.append('|-------------|----------|\n')
        report.append(f'| Pagina Acessivel | {"✓ Sim" if login_result["accessible"] else "✗ Nao"} |\n')
        report.append(f'| Status Code | {login_result["status_code"]} |\n')

        if login_result.get('html_analysis'):
            analysis = login_result['html_analysis']
            report.append(f'| Campo de Email | {"✓ Presente" if analysis["has_email_field"] else "✗ Ausente"} |\n')
            report.append(f'| Campo de Senha | {"✓ Presente" if analysis["has_password_field"] else "✗ Ausente"} |\n')
            report.append(f'| Botao de Submit | {"✓ Presente" if analysis["has_submit_button"] else "✗ Ausente"} |\n')
            report.append(f'| Token CSRF | {"✓ Presente" if analysis["has_csrf_token"] else "✗ Ausente"} |\n')
            if analysis.get('title'):
                report.append(f'| Titulo da Pagina | {analysis["title"]} |\n')
        report.append('\n')
    else:
        report.append(f'**Erro:** {login_result["error"]}\n\n')

    report.append('---\n\n')

    # Conclusions
    report.append('## Conclusoes\n\n')

    if failed == 0 and errors == 0:
        report.append('Todas as rotas protegidas estao corretamente configuradas com `LoginRequiredMixin`. ')
        report.append('Usuarios nao autenticados sao redirecionados para a pagina de login com o parametro "next" ')
        report.append('preservando a URL original, permitindo redirecionamento automatico apos login bem-sucedido.\n\n')
    else:
        report.append('ATENCAO: Foram detectadas falhas na protecao de rotas. ')
        report.append('Algumas rotas podem estar acessiveis sem autenticacao ou nao estao redirecionando corretamente.\n\n')

    report.append('### Recomendacoes\n\n')
    report.append('- Manter `LoginRequiredMixin` como primeiro mixin em todas as views protegidas\n')
    report.append('- Verificar configuracao de `LOGIN_URL` em settings.py\n')
    report.append('- Garantir que todas as rotas sensiveis requeiram autenticacao\n')
    report.append('- Implementar testes automatizados para verificar protecao de rotas\n')

    return ''.join(report)


def main():
    """Run tests and generate report."""
    print('Executando testes de protecao de rotas...\n')

    results = []
    for route_info in PROTECTED_ROUTES:
        print(f'Testando: {route_info["name"]} ({route_info["path"]})')
        result = test_route_protection(route_info)
        results.append(result)
        print(f'  Status: {result["status"]}\n')

    print('Testando pagina de login...')
    login_result = test_login_page()
    print(f'  Status: {login_result["status"]}\n')

    # Generate report
    report = generate_markdown_report(results, login_result)

    # Save report to file
    report_file = 'RELATORIO_TESTE_AUTENTICACAO.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f'Relatorio salvo em: {report_file}')
    print('\n' + '='*80)
    print('RESUMO')
    print('='*80)

    passed = sum(1 for r in results if r['status'] == 'PASSOU')
    failed = sum(1 for r in results if r['status'] == 'FALHOU')
    errors = sum(1 for r in results if r['status'] == 'ERRO')

    print(f'Total de testes: {len(results)}')
    print(f'Passou: {passed}')
    print(f'Falhou: {failed}')
    print(f'Erros: {errors}')

    if failed == 0 and errors == 0:
        print('\nTODOS OS TESTES PASSARAM!')
    else:
        print('\nFALHAS DETECTADAS!')

    return results, login_result


if __name__ == '__main__':
    main()

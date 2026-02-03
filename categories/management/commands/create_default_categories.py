from django.core.management.base import BaseCommand
from categories.models import Category


class Command(BaseCommand):
    help = 'Cria categorias padrão de receitas e despesas'

    def handle(self, *args, **options):
        # Categorias de despesas
        expense_categories = [
            {'name': 'Alimentação', 'color': '#EF4444'},
            {'name': 'Transporte', 'color': '#F97316'},
            {'name': 'Moradia', 'color': '#EAB308'},
            {'name': 'Saúde', 'color': '#22C55E'},
            {'name': 'Educação', 'color': '#3B82F6'},
            {'name': 'Lazer', 'color': '#8B5CF6'},
            {'name': 'Vestuário', 'color': '#EC4899'},
            {'name': 'Outros', 'color': '#6B7280'},
        ]

        # Categorias de receitas
        income_categories = [
            {'name': 'Salário', 'color': '#10B981'},
            {'name': 'Freelance', 'color': '#06B6D4'},
            {'name': 'Investimentos', 'color': '#8B5CF6'},
            {'name': 'Outros', 'color': '#6B7280'},
        ]

        created_count = 0
        existing_count = 0

        # Criar categorias de despesas
        self.stdout.write('\nCriando categorias de DESPESAS:')
        for category_data in expense_categories:
            category, created = Category.objects.get_or_create(
                user=None,
                name=category_data['name'],
                defaults={
                    'category_type': Category.EXPENSE,
                    'color': category_data['color'],
                    'is_default': True,
                    'is_active': True,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  Categoria "{category.name}" criada com sucesso'
                    )
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Categoria "{category.name}" ja existe'
                    )
                )
                existing_count += 1

        # Criar categorias de receitas
        self.stdout.write('\nCriando categorias de RECEITAS:')
        for category_data in income_categories:
            category, created = Category.objects.get_or_create(
                user=None,
                name=category_data['name'],
                defaults={
                    'category_type': Category.INCOME,
                    'color': category_data['color'],
                    'is_default': True,
                    'is_active': True,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  Categoria "{category.name}" criada com sucesso'
                    )
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Categoria "{category.name}" ja existe'
                    )
                )
                existing_count += 1

        # Resumo final
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f'\nResumo: {created_count} categorias criadas, '
                f'{existing_count} já existiam'
            )
        )
        self.stdout.write('=' * 50 + '\n')

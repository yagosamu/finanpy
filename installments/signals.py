from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Installment, InstallmentPlan, add_months


@receiver(post_save, sender=InstallmentPlan)
def create_installments_for_plan(sender, instance, created, **kwargs):
    if not created or instance.installments.exists():
        return

    installments = [
        Installment(
            plan=instance,
            number=number,
            due_date=add_months(instance.start_date, number - 1),
            amount=instance.installment_amount,
            status=Installment.PENDING,
        )
        for number in range(1, instance.installment_count + 1)
    ]
    Installment.objects.bulk_create(installments)

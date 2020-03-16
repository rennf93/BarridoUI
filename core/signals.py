import os
from .models import Snapshot, SnapshotRestore, ActiveWallet, ActiveWalletProcess, GenericCashin, ActiveWalletReport
from .tasks import (generate_snapshot_task, download_snapshot_task, restore_snapshot_task,
                    create_active_wallet_task, drop_database_task, active_wallet_start_task,
                    generic_cashin_init_task, generic_cashin_approve_task, active_wallet_report_task,
                    ActiveWalletReportManual, active_wallet_finish_task, snapshot_finish_task,
                    snapshot_restore_finish_task, delete_active_wallet_report)
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse


@receiver(post_save, sender=Snapshot)
def snapshot_handler(sender, instance, created, **kwargs):
    if created and not instance.dump and instance.generate:
        callback = "{}{}".format(
            getattr(settings, "APP_BASE_URL"),
            reverse("snapshot_callback", args=(instance.id,))
        )
        generate_snapshot_task.delay(instance.id, callback)
    elif created and not instance.dump and not instance.generate:
        download_snapshot_task.delay(instance.id)
    elif instance.status == "finished":
        snapshot_finish_task.delay()


@receiver(post_delete, sender=Snapshot)
def snapshot_delete_handler(sender, instance, **kwargs):
    if instance.status == "finished" and instance.dump:
        if os.path.isfile(instance.dump.path):
            os.remove(instance.dump.path)


@receiver(post_delete, sender=SnapshotRestore)
def snapshot_restore_delete_handler(sender, instance, **kwargs):
    drop_database_task.delay(instance.database_name)


@receiver(post_save, sender=SnapshotRestore)
def snapshot_restore_handler(sender, instance, created, **kwargs):
    if created:
        restore_snapshot_task.delay(instance.id)
    elif instance.status == "finished":
        snapshot_restore_finish_task.delay()


@receiver(post_save, sender=ActiveWallet)
def active_wallet_handler(sender, instance, created, **kwargs):
    if created:
        create_active_wallet_task.delay(instance.id)


@receiver(post_delete, sender=ActiveWallet)
def active_wallet_delete_handler(sender, instance, **kwargs):
    if instance.result:
        if os.path.isfile(instance.result.path):
            os.remove(instance.result.path)


@receiver(post_save, sender=ActiveWalletProcess)
def active_wallet_process_handler(sender, instance, created, **kwargs):
    if created:
        active_wallet_start_task.delay(instance.id)
    elif instance.status == "finished":
        active_wallet_finish_task.delay()


@receiver(post_save, sender=GenericCashin)
def generic_cashin_handler(sender, instance, created, **kwargs):    
    if created:
        generic_cashin_init_task.delay(instance.id)
    elif instance.status == "approved":
        generic_cashin_approve_task.delay(instance.id)


@receiver(post_save, sender=ActiveWalletReport)
def active_wallet_report_handler(sender, instance, created, **kwargs):
    if created and not instance.origin_report:
        ActiveWalletReportManual.delay(instance.id)
    elif created:
        ActiveWalletReportManual.delay(instance.id)


@receiver(post_delete, sender=ActiveWalletReport)
def active_wallet_report_delete_handler(sender, instance, **kwargs):
    delete_active_wallet_report.delay(instance.id)

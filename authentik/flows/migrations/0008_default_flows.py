# Generated by Django 3.0.3 on 2020-05-08 14:30

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

from authentik.flows.models import FlowDesignation
from authentik.stages.identification.models import UserFields
from authentik.stages.password import BACKEND_APP_PASSWORD, BACKEND_INBUILT, BACKEND_LDAP


def create_default_authentication_flow(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    Flow = apps.get_model("authentik_flows", "Flow")
    FlowStageBinding = apps.get_model("authentik_flows", "FlowStageBinding")
    PasswordStage = apps.get_model("authentik_stages_password", "PasswordStage")
    UserLoginStage = apps.get_model("authentik_stages_user_login", "UserLoginStage")
    IdentificationStage = apps.get_model("authentik_stages_identification", "IdentificationStage")
    db_alias = schema_editor.connection.alias

    identification_stage, _ = IdentificationStage.objects.using(db_alias).update_or_create(
        name="default-authentication-identification",
        defaults={
            "user_fields": [UserFields.E_MAIL, UserFields.USERNAME],
        },
    )

    password_stage, _ = PasswordStage.objects.using(db_alias).update_or_create(
        name="default-authentication-password",
        defaults={"backends": [BACKEND_INBUILT, BACKEND_LDAP, BACKEND_APP_PASSWORD]},
    )

    login_stage, _ = UserLoginStage.objects.using(db_alias).update_or_create(
        name="default-authentication-login"
    )

    flow, _ = Flow.objects.using(db_alias).update_or_create(
        slug="default-authentication-flow",
        designation=FlowDesignation.AUTHENTICATION,
        defaults={
            "name": "Welcome to authentik!",
        },
    )
    FlowStageBinding.objects.using(db_alias).update_or_create(
        target=flow,
        stage=identification_stage,
        defaults={
            "order": 10,
        },
    )
    FlowStageBinding.objects.using(db_alias).update_or_create(
        target=flow,
        stage=password_stage,
        defaults={
            "order": 20,
        },
    )
    FlowStageBinding.objects.using(db_alias).update_or_create(
        target=flow,
        stage=login_stage,
        defaults={
            "order": 100,
        },
    )


def create_default_invalidation_flow(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    Flow = apps.get_model("authentik_flows", "Flow")
    FlowStageBinding = apps.get_model("authentik_flows", "FlowStageBinding")
    UserLogoutStage = apps.get_model("authentik_stages_user_logout", "UserLogoutStage")
    db_alias = schema_editor.connection.alias

    UserLogoutStage.objects.using(db_alias).update_or_create(name="default-invalidation-logout")

    flow, _ = Flow.objects.using(db_alias).update_or_create(
        slug="default-invalidation-flow",
        designation=FlowDesignation.INVALIDATION,
        defaults={
            "name": "Logout",
        },
    )
    FlowStageBinding.objects.using(db_alias).update_or_create(
        target=flow,
        stage=UserLogoutStage.objects.using(db_alias).first(),
        defaults={
            "order": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("authentik_flows", "0007_auto_20200703_2059"),
        ("authentik_stages_user_login", "0001_initial"),
        ("authentik_stages_user_logout", "0001_initial"),
        ("authentik_stages_password", "0001_initial"),
        ("authentik_stages_identification", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_authentication_flow),
        migrations.RunPython(create_default_invalidation_flow),
    ]

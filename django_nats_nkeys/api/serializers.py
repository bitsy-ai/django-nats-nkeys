try:
    from rest_framework import serializers
    from ..models import (
        NatsOrganization,
        NatsOrganizationUser,
        NatsOrganizationApp,
        NatsOrganizationOwner,
        NatsRobotAccount,
        NatsRobotApp,
    )

    class NatsOrganizationSerializer(serializers.ModelSerializer):
        class Meta:
            model = NatsOrganization
            fields = "__all__"

    class NatsOrganizerionUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = NatsOrganizationUser
            fields = "_all__"

    class NatsOrganizationAppSerializer(serializers.ModelSerializer):
        organization = NatsOrganizationSerializer()
        organization_user = NatsOrganizerionUserSerializer()

        class Meta:
            model = NatsOrganizationApp
            fields = "_all__"

    class NatsOrganizationOwnerSerializer(serializers.ModelSerializer):
        class Meta:
            model = NatsOrganizationOwner
            fields = "_all__"

    class NatsRobotAccountSerializer(serializers.ModelSerializer):
        class Meta:
            model = NatsRobotAccount
            fields = "_all__"

    class NatsRobotAppSerializer(serializers.ModelSerializer):
        class Meta:
            model = NatsRobotApp
            fields = "__all__"


except ImportError:
    pass

from tortoise import fields
from tortoise.models import Model


class InsuranceRate(Model):
    cargo_type = fields.CharField(max_length=255, null=False)
    rate = fields.FloatField(null=False)
    date = fields.DateField(null=False)

    def __str__(self):
        return self.cargo_type

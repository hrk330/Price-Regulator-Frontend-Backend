# Generated manually for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('violations', '0002_violationcheckreport'),
    ]

    operations = [
        # Add composite indexes for frequently queried combinations
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_violation_status_severity ON violations_violation (status, severity);",
            reverse_sql="DROP INDEX IF EXISTS idx_violation_status_severity;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_violation_created_at ON violations_violation (created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_violation_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_violationcheckreport_compliance_status ON violations_violationcheckreport (compliance_status, check_date DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_violationcheckreport_compliance_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_violationcheckreport_has_violation ON violations_violationcheckreport (has_violation, check_date DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_violationcheckreport_has_violation;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_violationcheckreport_scraped_product ON violations_violationcheckreport (scraped_product_id, check_date DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_violationcheckreport_scraped_product;"
        ),
    ]
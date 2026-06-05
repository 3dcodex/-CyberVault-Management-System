from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from vault.models import Credential
from vulnerabilities.models import VulnerabilityReport
from .forms import RegisterForm

_MAX_LOGIN_ATTEMPTS = 5
_LOCKOUT_SECONDS    = 300  # 5 minutes


def _get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR', '')

staff_required = user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')


# ── Auth ──────────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created. Welcome, {user.username}!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        ip       = _get_client_ip(request)
        cache_key = f'login_fail_{ip}'
        attempts  = cache.get(cache_key, 0)

        if attempts >= _MAX_LOGIN_ATTEMPTS:
            messages.error(request, 'Too many failed attempts. Please wait 5 minutes before trying again.')
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            cache.delete(cache_key)
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next', '')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('dashboard')

        cache.set(cache_key, attempts + 1, _LOCKOUT_SECONDS)
        messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')


# ── User ──────────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


@login_required
def dashboard_view(request):
    user = request.user
    context = {
        'total_passwords': Credential.objects.filter(owner=user).count(),
        'open_vulns':      VulnerabilityReport.objects.filter(reporter=user, status='Open').count(),
        'fixed_vulns':     VulnerabilityReport.objects.filter(reporter=user, status='Fixed').count(),
    }
    if user.is_staff:
        context['total_users'] = User.objects.filter(is_active=True).count()
    return render(request, 'accounts/dashboard.html', context)


# ── Admin user management ─────────────────────────────────────────────────────

@login_required
@staff_required
def admin_user_list(request):
    search = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    users = User.objects.annotate(
        credential_count=Count('credentials', distinct=True),
        report_count=Count('vulnerability_reports', distinct=True),
    ).order_by('date_joined')

    if search:
        users = users.filter(username__icontains=search) | users.filter(email__icontains=search)
        users = users.distinct()

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'staff':
        users = users.filter(is_staff=True)

    total_count    = User.objects.count()
    active_count   = User.objects.filter(is_active=True).count()
    inactive_count = User.objects.filter(is_active=False).count()
    staff_count    = User.objects.filter(is_staff=True).count()

    return render(request, 'accounts/admin_users.html', {
        'users':          users,
        'search':         search,
        'status_filter':  status_filter,
        'total_count':    total_count,
        'active_count':   active_count,
        'inactive_count': inactive_count,
        'staff_count':    staff_count,
    })


@login_required
@staff_required
def admin_toggle_user(request, pk):
    if request.method != 'POST':
        return redirect('admin_user_list')

    target = get_object_or_404(User, pk=pk)

    if target == request.user:
        messages.error(request, 'You cannot change your own account status.')
        return redirect('admin_user_list')

    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Only superusers can modify other superuser accounts.')
        return redirect('admin_user_list')

    target.is_active = not target.is_active
    target.save(update_fields=['is_active'])
    action = 'activated' if target.is_active else 'deactivated'
    messages.success(request, f'Account "{target.username}" {action}.')
    return redirect('admin_user_list')


@login_required
@staff_required
def admin_delete_user(request, pk):
    target = get_object_or_404(User, pk=pk)

    if target == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('admin_user_list')

    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Only superusers can delete other superuser accounts.')
        return redirect('admin_user_list')

    if request.method == 'POST':
        username = target.username
        target.delete()
        messages.success(request, f'Account "{username}" permanently deleted.')
        return redirect('admin_user_list')

    return render(request, 'accounts/admin_user_confirm_delete.html', {'target': target})

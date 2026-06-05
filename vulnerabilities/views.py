from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import VulnerabilityReport
from .forms import VulnerabilityReportForm


def _can_modify(user, report):
    return user.is_staff or report.reporter == user


@login_required
def report_list(request):
    reports = VulnerabilityReport.objects.select_related('reporter').order_by('-created_at')

    severity_filter = request.GET.get('severity', '')
    status_filter   = request.GET.get('status', '')
    if severity_filter:
        reports = reports.filter(severity=severity_filter)
    if status_filter:
        reports = reports.filter(status=status_filter)

    return render(request, 'vulnerabilities/report_list.html', {
        'reports':          reports,
        'severity_filter':  severity_filter,
        'status_filter':    status_filter,
        'severity_choices': VulnerabilityReport.Severity.choices,
        'status_choices':   VulnerabilityReport.Status.choices,
    })


@login_required
def report_detail(request, pk):
    report = get_object_or_404(VulnerabilityReport.objects.select_related('reporter'), pk=pk)
    return render(request, 'vulnerabilities/report_detail.html', {
        'report':      report,
        'can_modify':  _can_modify(request.user, report),
    })


@login_required
def report_add(request):
    if request.method == 'POST':
        form = VulnerabilityReportForm(request.POST, user=request.user)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            messages.success(request, f'Report "{report.title}" submitted.')
            return redirect('vulnerabilities:report_detail', pk=report.pk)
    else:
        form = VulnerabilityReportForm(user=request.user)
    return render(request, 'vulnerabilities/report_form.html', {'form': form, 'action': 'Add'})


@login_required
def report_edit(request, pk):
    report = get_object_or_404(VulnerabilityReport, pk=pk)
    if not _can_modify(request.user, report):
        raise PermissionDenied
    if request.method == 'POST':
        form = VulnerabilityReportForm(request.POST, instance=report, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Report "{report.title}" updated.')
            return redirect('vulnerabilities:report_detail', pk=report.pk)
    else:
        form = VulnerabilityReportForm(instance=report, user=request.user)
    return render(request, 'vulnerabilities/report_form.html', {
        'form':   form,
        'action': 'Edit',
        'report': report,
    })


@login_required
def report_delete(request, pk):
    report = get_object_or_404(VulnerabilityReport, pk=pk)
    if not _can_modify(request.user, report):
        raise PermissionDenied
    if request.method == 'POST':
        title = report.title
        report.delete()
        messages.success(request, f'Report "{title}" deleted.')
        return redirect('vulnerabilities:report_list')
    return render(request, 'vulnerabilities/report_confirm_delete.html', {'report': report})

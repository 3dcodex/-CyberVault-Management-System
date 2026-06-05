from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Credential
from .forms import CredentialForm


@login_required
def credential_list(request):
    credentials = Credential.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'vault/credential_list.html', {'credentials': credentials})


@login_required
def credential_add(request):
    if request.method == 'POST':
        form = CredentialForm(request.POST)
        if form.is_valid():
            credential = form.save(commit=False)
            credential.owner = request.user
            credential.save()
            messages.success(request, f'"{credential.site_name}" saved to vault.')
            return redirect('vault:credential_list')
    else:
        form = CredentialForm()
    return render(request, 'vault/credential_form.html', {'form': form, 'action': 'Add'})


@login_required
def credential_edit(request, pk):
    credential = get_object_or_404(Credential, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = CredentialForm(request.POST, instance=credential)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{credential.site_name}" updated.')
            return redirect('vault:credential_list')
    else:
        form = CredentialForm(instance=credential)
    return render(request, 'vault/credential_form.html', {
        'form': form,
        'action': 'Edit',
        'credential': credential,
    })


@login_required
def credential_delete(request, pk):
    credential = get_object_or_404(Credential, pk=pk, owner=request.user)
    if request.method == 'POST':
        name = credential.site_name
        credential.delete()
        messages.success(request, f'"{name}" removed from vault.')
        return redirect('vault:credential_list')
    return render(request, 'vault/credential_confirm_delete.html', {'credential': credential})

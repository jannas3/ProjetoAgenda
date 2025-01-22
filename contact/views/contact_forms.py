from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from contact.forms import ContactForm
from contact.models import Contact
from django.contrib import messages  



@login_required(login_url='contact:login')
def create(request):
    form_action = reverse('contact:create')

    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)

        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = request.user
            contact.save()
            messages.success(request, 'Contato criado com sucesso!')  # Adicionando mensagem de sucesso
            return redirect('contact:index')  # Redireciona para a página principal

        return render(
            request,
            'contact/create.html',
            context
        )

    context = {
        'form': ContactForm(),
        'form_action': form_action,
    }

    return render(
        request,
        'contact/create.html',
        context
    )

@login_required(login_url='contact:login')
def update(request, contact_id):
    # Obtém o contato a ser atualizado
    contact = get_object_or_404(Contact, pk=contact_id, show=True, owner=request.user)
    
    # Definindo a ação do formulário de atualização
    form_action = reverse('contact:update', args=(contact_id,))

    if request.method == 'POST':
        # Cria o formulário com os dados recebidos via POST e o contato a ser atualizado
        form = ContactForm(request.POST, request.FILES, instance=contact)

        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            # Salva as alterações no contato
            form.save()
            # Mensagem de sucesso após atualização
            messages.success(request, 'Contato atualizado com sucesso!')
            # Redireciona para a página de índice após a atualização
            return redirect('contact:index')

        # Caso o formulário não seja válido, renderiza a página de atualização novamente
        return render(request, 'contact/create.html', context)

    # Se o método for GET, exibe o formulário com os dados do contato
    context = {
        'form': ContactForm(instance=contact),
        'form_action': form_action,
    }

    return render(request, 'contact/create.html', context)


@login_required(login_url='contact:login')
def delete(request, contact_id):
    contact = get_object_or_404(
        Contact, pk=contact_id, show=True, owner=request.user
    )
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        contact.delete()
        messages.success(request, 'Contato excluido com sucesso!')
            # Redireciona para a página de índice após a atualização
        return redirect('contact:index')

    return render(
        request,
        'contact/contact.html',
        {
            'contact': contact,
            'confirmation': confirmation,
        }
    )

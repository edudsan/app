document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://localhost:8000';

    // As variáveis globais são declaradas aqui.
    let navLinks, contentSections, modals, forms;

    // --- Funções Auxiliares ---
    function showNotification(message, type = 'success') {
        alert(message);
    }

    function createTable(headers) {
        const table = document.createElement('table');
        table.innerHTML = `<thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody></tbody>`;
        return table;
    }

    // --- Funções de Renderização ---
    const renderers = {
        clientes: (data, container) => {
            container.innerHTML = '';
            if (!data.length) { container.innerHTML = '<p>Nenhum cliente cadastrado.</p>'; return; }
            const table = createTable(['Nome', 'Documento', 'E-mail', 'Telefone', 'Ações']);
            const tbody = table.querySelector('tbody');
            tbody.innerHTML = data.map(c => `
                <tr>
                    <td>${c.nome}</td>
                    <td>${c.cpf || c.cnpj || 'N/A'}</td>
                    <td>${c.email}</td>
                    <td>${c.telefone || 'N/A'}</td>
                    <td class="actions-cell">
                        <button class="btn-edit" data-type="cliente" data-id="${c.pessoa_id}">Editar</button>
                        <button class="btn-delete" data-type="clientes" data-id="${c.pessoa_id}">Excluir</button>
                    </td>
                </tr>`).join('');
            container.appendChild(table);
        },
        veiculos: (data, container) => {
            container.innerHTML = '';
            if (!data.length) { container.innerHTML = '<p>Nenhum veículo cadastrado.</p>'; return; }
            const table = createTable(['Placa', 'Modelo', 'Marca', 'Diária', 'Ações']);
            const tbody = table.querySelector('tbody');
            tbody.innerHTML = data.map(v => `
                <tr>
                    <td>${v.placa}</td>
                    <td>${v.modelo}</td>
                    <td>${v.marca || 'N/A'}</td>
                    <td>R$ ${v.valor_diaria.toFixed(2)}</td>
                    <td class="actions-cell">
                        <button class="btn-edit" data-type="veiculo" data-id="${v.veiculo_id}">Editar</button>
                        <button class="btn-delete" data-type="veiculos" data-id="${v.veiculo_id}">Excluir</button>
                    </td>
                </tr>`).join('');
            container.appendChild(table);
        },
        reservas: (data, container) => {
            container.innerHTML = '';
            if (!data.length) { container.innerHTML = '<p>Nenhuma reserva encontrada.</p>'; return; }
            const table = createTable(['Cliente', 'Veículo', 'Período', 'Valor Total', 'Ações']);
            const tbody = table.querySelector('tbody');
            tbody.innerHTML = data.map(r => `
                <tr>
                    <td>${r.cliente.nome}</td>
                    <td>${r.veiculo.modelo} (${r.veiculo.placa})</td>
                    <td>${new Date(r.data_inicio + 'T00:00:00').toLocaleDateString()} - ${new Date(r.data_fim + 'T00:00:00').toLocaleDateString()}</td>
                    <td>R$ ${r.valor_total.toFixed(2)}</td>
                    <td class="actions-cell">
                        <button class="btn-edit" data-type="reserva" data-id="${r.reserva_id}">Editar</button>
                        <button class="btn-delete" data-type="reservas" data-id="${r.reserva_id}">Excluir</button>
                    </td>
                </tr>`).join('');
            container.appendChild(table);
        }
    };
    
    async function fetchAndRenderData(sectionName) {
        const endpoint = sectionName === 'clientes' ? '/clientes' : `/${sectionName}`;
        const container = document.getElementById(`${sectionName}-table-container`);
        if (!container) return;
        try {
            const response = await fetch(`${API_URL}${endpoint}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            renderers[sectionName](data, container);
        } catch (error) {
            showNotification(`Falha ao buscar ${sectionName}: ${error.message}`, 'error');
            container.innerHTML = `<p>Erro ao carregar dados.</p>`;
        }
    }
    
    async function refreshAllTables() {
        await Promise.all([
            fetchAndRenderData('clientes'),
            fetchAndRenderData('veiculos'),
            fetchAndRenderData('reservas')
        ]);
    }

    function populateForm(type, data) {
        const form = forms[type];
        if (!form) return;
        if (type === 'cliente') {
            form.querySelector('#cliente-nome').value = data.nome;
            form.querySelector('#cliente-email').value = data.email;
            form.querySelector('#cliente-email').readOnly = true;
            form.querySelector('#cliente-telefone').value = data.telefone || '';
            
            if (data.endereco) {
                form.querySelector('#endereco-rua').value = data.endereco.rua || '';
                form.querySelector('#endereco-bairro').value = data.endereco.bairro || '';
                form.querySelector('#endereco-cidade').value = data.endereco.cidade || '';
                form.querySelector('#endereco-estado').value = data.endereco.estado || '';
                form.querySelector('#endereco-numero').value = data.endereco.numero || '';
            }
            
            const tipoPessoaSelect = form.querySelector('#cliente-tipo-pessoa');
            const campoCpf = form.querySelector('#campo-cpf');
            const campoCnpj = form.querySelector('#campo-cnpj');
            const inputCpf = form.querySelector('#cliente-cpf');
            const inputCnpj = form.querySelector('#cliente-cnpj');

            tipoPessoaSelect.disabled = true;
            if (data.tipo_pessoa === 'PF') {
                tipoPessoaSelect.value = 'PF';
                inputCpf.value = data.cpf;
                inputCpf.readOnly = true;
                campoCpf.style.display = 'block';
                campoCnpj.style.display = 'none';
            } else {
                tipoPessoaSelect.value = 'PJ';
                inputCnpj.value = data.cnpj;
                inputCnpj.readOnly = true;
                campoCpf.style.display = 'none';
                campoCnpj.style.display = 'block';
            }
            
        } else if (type === 'veiculo') {
            form.querySelector('#veiculo-placa').value = data.placa;
            form.querySelector('#veiculo-placa').readOnly = true;
            form.querySelector('#veiculo-modelo').value = data.modelo;
            form.querySelector('#veiculo-marca').value = data.marca || '';
            form.querySelector('#veiculo-ano').value = data.ano || '';
            form.querySelector('#veiculo-diaria').value = data.valor_diaria;
        } else if (type === 'reserva') {
            form.querySelector('#reserva-inicio').value = data.data_inicio;
            form.querySelector('#reserva-fim').value = data.data_fim;
            form.querySelector('#reserva-tipo').value = data.tipo_reserva;
            form.querySelector('#reserva-cliente').disabled = true;
            form.querySelector('#reserva-veiculo').disabled = true;
            populateReservaDropdowns({clienteId: data.cliente_id, veiculoId: data.veiculo_id});
        }
    }

    async function openModal(type, id = null) {
        const form = forms[type];
        const modal = modals[type];
        if (!form || !modal) { return; }
        form.reset();

        form.querySelectorAll('input').forEach(input => input.readOnly = false);
        form.querySelectorAll('select').forEach(select => select.disabled = false);

        const idInput = form.querySelector(`#${type}-id`);
        const modalTitle = form.querySelector('h3');
        
        const enderecoFields = form.querySelectorAll('hr, h4, #endereco-rua, #endereco-bairro, #endereco-cidade, #endereco-estado, #endereco-numero');
        
        if (id) {
            modalTitle.textContent = `Editar ${type.charAt(0).toUpperCase() + type.slice(1)}`;
            if (idInput) idInput.value = id;
            
            if (type === 'cliente') enderecoFields.forEach(el => el.style.display = 'block');
            
            const endpoint = type === 'cliente' ? '/clientes' : `/${type}s`;
            try {
                const response = await fetch(`${API_URL}${endpoint}/${id}`);
                if (!response.ok) throw new Error("Item não encontrado");
                const data = await response.json();
                populateForm(type, data);
            } catch (e) {
                showNotification("Erro ao carregar dados para edição.", "error");
                return;
            }
        } else {
            modalTitle.textContent = `Adicionar Novo ${type.charAt(0).toUpperCase() + type.slice(1)}`;
            if (idInput) idInput.value = '';

            if (type === 'cliente') {
                enderecoFields.forEach(el => el.style.display = 'block');
                document.getElementById('cliente-tipo-pessoa').dispatchEvent(new Event('change'));
            }
            if (type === 'reserva') {
                await populateReservaDropdowns();
            }
        }
        
        modal.showModal();
    }
    
    async function populateReservaDropdowns(selected = {}) {
        const clienteSelect = document.getElementById('reserva-cliente');
        const veiculoSelect = document.getElementById('reserva-veiculo');
        try {
            const [clientesRes, veiculosRes] = await Promise.all([
                fetch(`${API_URL}/clientes`), 
                fetch(`${API_URL}/veiculos`)
            ]);
            const clientes = await clientesRes.json();
            const veiculos = await veiculosRes.json();
            clienteSelect.innerHTML = '<option value="">Selecione um cliente...</option>' + clientes.map(c => `<option value="${c.pessoa_id}" ${selected.clienteId == c.pessoa_id ? 'selected' : ''}>${c.nome}</option>`).join('');
            veiculoSelect.innerHTML = '<option value="">Selecione um veículo...</option>' + veiculos.map(v => `<option value="${v.veiculo_id}" ${selected.veiculoId == v.veiculo_id ? 'selected' : ''}>${v.modelo} (${v.placa})</option>`).join('');
        } catch (error) { showNotification("Erro ao carregar dados para reserva.", 'error'); }
    }

    async function handleFormSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const type = form.id.replace('form-', '');
        
        const id = form.querySelector(`#${type}-id`)?.value;
        const method = id ? 'PUT' : 'POST';
        let url, body;

        if (type === 'cliente') {
            body = {
                nome: form.querySelector('#cliente-nome').value,
                telefone: form.querySelector('#cliente-telefone').value,
                endereco: {
                    rua: form.querySelector('#endereco-rua').value,
                    bairro: form.querySelector('#endereco-bairro').value,
                    cidade: form.querySelector('#endereco-cidade').value,
                    estado: form.querySelector('#endereco-estado').value,
                    numero: parseInt(form.querySelector('#endereco-numero').value) || null
                }
            };
            if (!id) {
                body.email = form.querySelector('#cliente-email').value;
                const tipoPessoa = form.querySelector('#cliente-tipo-pessoa').value;
                if (tipoPessoa === 'PF') {
                    url = '/clientes/pf';
                    body.cpf = form.querySelector('#cliente-cpf').value;
                    body.tipo_pessoa = 'PF';
                } else {
                    url = '/clientes/pj';
                    body.cnpj = form.querySelector('#cliente-cnpj').value;
                    body.tipo_pessoa = 'PJ';
                }
            } else {
                url = `/clientes/${id}`;
            }
        } else if (type === 'veiculo') {
            body = {
                modelo: form.querySelector('#veiculo-modelo').value,
                marca: form.querySelector('#veiculo-marca').value,
                ano: parseInt(form.querySelector('#veiculo-ano').value) || null,
                valor_diaria: parseFloat(form.querySelector('#veiculo-diaria').value)
            };
             if (!id) {
                 body.placa = form.querySelector('#veiculo-placa').value;
             }
             url = id ? `/veiculos/${id}` : '/veiculos';
        } else if (type === 'reserva') {
            body = {
                data_inicio: form.querySelector('#reserva-inicio').value,
                data_fim: form.querySelector('#reserva-fim').value,
                tipo_reserva: form.querySelector('#reserva-tipo').value
            };
             if (!id) {
                body.cliente_id = parseInt(form.querySelector('#reserva-cliente').value);
                body.veiculo_id = parseInt(form.querySelector('#reserva-veiculo').value);
             }
             url = id ? `/reservas/${id}` : '/reservas';
        }

        try {
            const response = await fetch(`${API_URL}${url}`, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro desconhecido');
            }
            if (modals[type]) modals[type].close();
            refreshAllTables();
            showNotification(`${type.charAt(0).toUpperCase() + type.slice(1)} salvo com sucesso!`);
        } catch (error) {
            showNotification(`Erro ao salvar: ${error.message}`, 'error');
        }
    }
    
    function setupEventListeners() {
        forms.cliente?.addEventListener('submit', handleFormSubmit);
        forms.veiculo?.addEventListener('submit', handleFormSubmit);
        forms.reserva?.addEventListener('submit', handleFormSubmit);
        forms.buscaVeiculos?.addEventListener('submit', handleBuscaVeiculos);
        forms.relatorioFaturamento?.addEventListener('submit', handleRelatorioFaturamento);
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                showSection(e.target.dataset.section);
            });
        });

        document.addEventListener('click', (e) => {
            const target = e.target;
            const type = target.dataset.type;
            const id = target.dataset.id;
            
            if (target.matches('.btn-add')) openModal(type);
            if (target.matches('.btn-edit')) openModal(type, id);
            if (target.matches('.btn-close')) target.closest('dialog')?.close();

            if (target.matches('.btn-delete')) {
                const endpointType = target.dataset.type;
                if (!confirm(`Tem certeza que deseja excluir? Esta ação não pode ser desfeita.`)) return;
                fetch(`${API_URL}/${endpointType}/${id}`, { method: 'DELETE' })
                    .then(response => {
                        if (response.ok) {
                            refreshAllTables();
                            showNotification('Item excluído com sucesso.');
                        } else {
                            response.json().then(error => showNotification(`Não foi possível excluir: ${error.detail}`, 'error'));
                        }
                    });
            }
        });

        document.getElementById('cliente-tipo-pessoa')?.addEventListener('change', (e) => {
            const isPF = e.target.value === 'PF';
            document.getElementById('campo-cpf').style.display = isPF ? 'block' : 'none';
            document.getElementById('campo-cnpj').style.display = isPF ? 'none' : 'block';
            document.getElementById('cliente-cpf').required = isPF;
            document.getElementById('cliente-cnpj').required = !isPF;
        });
    }

    async function handleBuscaVeiculos(e) {
        e.preventDefault();
        document.getElementById('relatorio-faturamento-result-container').innerHTML = '';
        const inicio = document.getElementById('busca-inicio').value;
        const fim = document.getElementById('busca-fim').value;
        if (!inicio || !fim) {
            showNotification("Por favor, preencha as duas datas.", "error");
            return;
        }
        try {
            const response = await fetch(`${API_URL}/veiculos/disponiveis/?data_inicio=${inicio}&data_fim=${fim}`);
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail);
            }
            const veiculos = await response.json();
            const container = document.getElementById('busca-veiculos-result-container');
            let contentHTML = '<h4>Resultado da Busca: Veículos Disponíveis</h4>';
            
            if (veiculos.length === 0) {
                contentHTML += '<p>Nenhum veículo disponível para o período selecionado.</p>';
            } else {
                const table = createTable(['Placa', 'Modelo', 'Marca', 'Diária']);
                const tbody = table.querySelector('tbody');
                tbody.innerHTML = veiculos.map(v => `
                    <tr>
                        <td>${v.placa}</td>
                        <td>${v.modelo}</td>
                        <td>${v.marca || 'N/A'}</td>
                        <td>R$ ${v.valor_diaria.toFixed(2)}</td>
                    </tr>`).join('');
                contentHTML += table.outerHTML;
            }
            container.innerHTML = `<div class="result-card">${contentHTML}</div>`;
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }

    async function handleRelatorioFaturamento(e) {
        e.preventDefault();
        document.getElementById('busca-veiculos-result-container').innerHTML = '';
        const inicio = document.getElementById('relatorio-inicio').value;
        const fim = document.getElementById('relatorio-fim').value;
        if (!inicio || !fim) {
            showNotification("Por favor, preencha as duas datas.", "error");
            return;
        }
        try {
            const response = await fetch(`${API_URL}/reservas/relatorio/faturamento/?data_inicio=${inicio}&data_fim=${fim}`);
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail);
            }
            const relatorio = await response.json();
            const container = document.getElementById('relatorio-faturamento-result-container');
            
            const reportHTML = `
                <h4>Resultado: Relatório de Faturamento</h4>
                <div class="report-content">
                    <p><strong>Período:</strong> ${new Date(relatorio.periodo_inicio+'T00:00:00').toLocaleDateString()} a ${new Date(relatorio.periodo_fim+'T00:00:00').toLocaleDateString()}</p>
                    <p><strong>Total de Reservas:</strong> ${relatorio.total_reservas}</p>
                    <p><strong>Faturamento Total:</strong> R$ ${relatorio.faturamento_total.toFixed(2)}</p>
                </div>
            `;
            container.innerHTML = `<div class="result-card">${reportHTML}</div>`;
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }

    function showSection(sectionId) {
        contentSections.forEach(s => s.classList.remove('active'));
        navLinks.forEach(l => l.classList.remove('active'));
        
        const newActiveSection = document.getElementById(sectionId);
        const newActiveLink = document.querySelector(`.nav-link[data-section="${sectionId}"]`);
        
        if (newActiveSection) newActiveSection.classList.add('active');
        if (newActiveLink) newActiveLink.classList.add('active');

        const sectionName = sectionId.replace('-section', '');
        
        const buscaContainer = document.getElementById('busca-veiculos-result-container');
        const relatorioContainer = document.getElementById('relatorio-faturamento-result-container');

        if (sectionId !== 'extras-section') {
            if(buscaContainer) buscaContainer.innerHTML = '';
            if(relatorioContainer) relatorioContainer.innerHTML = '';
        }

        if(sectionName !== 'extras') {
            fetchAndRenderData(sectionName);
        }
    }
    
    function initializeApp() {
        navLinks = document.querySelectorAll('.nav-link');
        contentSections = document.querySelectorAll('.content-section');
        modals = {
            cliente: document.getElementById('modal-cliente'),
            veiculo: document.getElementById('modal-veiculo'),
            reserva: document.getElementById('modal-reserva')
        };
        forms = {
            cliente: document.getElementById('form-cliente'),
            veiculo: document.getElementById('form-veiculo'),
            reserva: document.getElementById('form-reserva'),
            buscaVeiculos: document.getElementById('form-busca-veiculos'),
            relatorioFaturamento: document.getElementById('form-relatorio-faturamento')
        };
        
        setupEventListeners();
        showSection('clientes-section');
    }
    
    initializeApp();
});
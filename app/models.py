from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class RotaManager(models.Manager):
    def criar_rota(self, ids_entregas, dados_api):
        if not ids_entregas:
            return (False, "Nenhuma entrega selecionada.")
        try:
            with transaction.atomic(): #procura por motoristas e veiculos livres
                #pega os motorista e veículos q estão na rota planejada ou em execução e agrupa
                motoristas_ocupados_ids = Rota.objects.filter(status__in=['PLANEJADA', 'EM_ROTA']).values_list('motorista_id', flat=True)
                veiculos_ocupados_ids = Rota.objects.filter(status__in=['PLANEJADA', 'EM_ROTA']).values_list('veiculo_id', flat=True)

                #pega os motoristas e veículos livres (q n entraram no agrupamento acima) e escolhe o primeiro pra atribuir à entrega
                motorista_disponivel = PerfilMotorista.objects.select_for_update().filter(disponivel=True).exclude(id__in=motoristas_ocupados_ids).first()
                veiculo_disponivel = Veiculo.objects.select_for_update().filter(status='DISPONIVEL').exclude(id__in=veiculos_ocupados_ids).first()

                # mas e se não tiver nenhum disponível? chora ;)
                if not veiculo_disponivel or not motorista_disponivel:
                    return (False, "Nenhum veículo ou motorista disponível no momento.")
                
                inicio_previsto = timezone.now() + timezone.timedelta(minutes=15)
                fim_previsto = inicio_previsto + timezone.timedelta(minutes=dados_api['duracao_minutos'])

                #cria rota
                nova_rota = self.model.objects.create(
                    veiculo=veiculo_disponivel,
                    motorista=motorista_disponivel,
                    status='PLANEJADA',
                    distancia_total_km=dados_api.get('distancia_km'),
                    duracao_estimada_minutos=dados_api.get('duracao_minutos'),
                    trajeto_polyline=dados_api.get('trajeto_polyline'),
                    data_inicio_prevista=inicio_previsto,
                    data_fim_prevista=fim_previsto
                )

                # associa entregas à rota
                entregas_alocar = Entrega.objects.filter(id__in=ids_entregas, status='EM_SEPARACAO')
                if not entregas_alocar.exists():
                    raise Exception("Entregas selecionadas não estão mais disponíveis para alocação.")
                
                entregas_alocar.update(rota=nova_rota, status='EM_SEPARACAO')

                msg = f"Rota #{nova_rota.id} criada com {entregas_alocar.count()} entregas. Distância: {nova_rota.distancia_total_km} km."
                return (True, msg)

        except Exception as e:
            return (False, f"Erro ao criar a rota: {e}")

class PerfilCliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_empresa = models.CharField(max_length=100, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'Perfil de Cliente para {self.user.username}'

class Veiculo(models.Model):
    status_veiculo = [
        ('DISPONIVEL', 'Disponível'),
        ('EM_ENTREGA', 'Em Entrega'),
        ('EM_MANUTENCAO', 'Em Manutenção')
    ]

    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=100)
    km = models.PositiveIntegerField()
    autonomia = models.DecimalField(max_digits=5, decimal_places=2)
    ultimaManutencao = models.DateField()
    status = models.CharField(max_length=15, choices=status_veiculo, default='DISPONIVEL')
    localizacao_atual = models.ForeignKey('Coordenada', on_delete=models.SET_NULL, null=True, blank=True)
    
    #preventiva
    def precisa_manutencao(self):
        if not self.ultimaManutencao:
            return True
        
        dias_desde_manutencao = (timezone.now().date() - self.ultimaManutencao).days
        return dias_desde_manutencao > 180 #a cada 6 meses

    def __str__(self):
        return f"{self.modelo} ({self.placa})"

class PerfilMotorista(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    num_cnh = models.CharField(max_length=20, unique=True)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Rota(models.Model):
    status_rota = [
        ('PLANEJADA', 'Planejada'),
        ('EM_ROTA', 'Em Rota'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada')
    ]

    distancia_total_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duracao_estimada_minutos = models.PositiveIntegerField(null=True, blank=True)

    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT, related_name='rotas')
    motorista = models.ForeignKey(PerfilMotorista, on_delete=models.PROTECT, related_name='rotas')
    status = models.CharField(max_length=20, choices=status_rota, default='PLANEJADA')

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_inicio_prevista = models.DateTimeField(null=True, blank=True)
    data_fim_prevista = models.DateTimeField(null=True, blank=True)

    data_inicio_real = models.DateTimeField(null=True, blank=True)
    data_fim_real = models.DateTimeField(null=True, blank=True)

    trajeto_polyline = models.TextField(blank=True, null=True)

    objects = RotaManager()

    def __str__(self):
        return f"Rota #{self.id} | Veículo: {self.veiculo.modelo} - {self.veiculo.placa}"

class Manutencao(models.Model):
    TIPO_MANUTENCAO = [
        ("PREVENTIVA", 'Preventiva'),
        ("CORRETIVA", 'Corretiva'),
    ]

    veiculo = models.ForeignKey('Veiculo', on_delete=models.CASCADE)
    motorista = models.ForeignKey('PerfilMotorista', on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_MANUTENCAO)
    descricao = models.TextField()
    data = models.DateField()
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_MANUTENCAO = [
        ("SOLICITADA", "Solicitada"),
        ("PENDENTE", "Pendente"),
        ("CONCLUIDA", "Concluída"),
    ]
    status = models.CharField(max_length=20, default="PENDENTE", choices=STATUS_MANUTENCAO)   

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.veiculo.modelo} ({self.data})"

class Abastecimento(models.Model):
    litros = models.FloatField()
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    dataAbastecimento = models.DateField()
    veiculo = models.ForeignKey('Veiculo', on_delete=models.SET_NULL, null=True, blank=True)
    motorista = models.ForeignKey('PerfilMotorista', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.veiculo} - {self.litros}L | {self.dataAbastecimento}"

class Coordenada(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    rua = models.CharField(max_length=255, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=50, blank=True)
    cep = models.CharField(max_length=10, blank=True)

    endereco_completo = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.endereco_completo or f"({self.latitude:.4f}, {self.longitude:.4f})"

class Entrega(models.Model):
    STATUS_ENTREGA = [
        ("PENDENTE", "Pendente"),
        ("EM_SEPARACAO", "Em Separação"),
        ("EM_ROTA", "Em Rota"),
        ("ENTREGUE", "Entregue"),
        ("PROBLEMA", "Problema"),
    ]

    cliente = models.ForeignKey(PerfilCliente, on_delete=models.SET_NULL, null=True, blank=True)
    origem = models.ForeignKey(Coordenada, on_delete=models.SET_NULL, null=True, related_name="origens")
    destino = models.ForeignKey(Coordenada, on_delete=models.SET_NULL, null=True, related_name="destinos")

    descricao_carga = models.CharField(max_length=255, help_text="Ex: 2 caixas de eletrônicos")
    peso_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Peso total da carga em Kg")
    volume_m3 = models.DecimalField(max_digits=10, decimal_places=2, help_text="Volume total da carga em metros cúbicos (m³)")
    fragil = models.BooleanField(default=False, verbose_name="Carga Frágil?")
    
    nome_destinatario = models.CharField(max_length=100)
    telefone_destinatario = models.CharField(max_length=20)
    observacoes_entrega = models.TextField(blank=True, help_text="Ex: Deixar na portaria, cuidado ao manusear.")
    
    status = models.CharField(max_length=20, choices=STATUS_ENTREGA, default="PENDENTE")
    rota = models.ForeignKey(Rota, on_delete=models.SET_NULL, null=True, blank=True, related_name='entregas')
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_entrega_prevista = models.DateTimeField(null=True, blank=True)
    data_entrega_real = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Entrega #{self.id} para {self.cliente}"

class HistoricoEntrega(models.Model):
    entrega = models.ForeignKey(Entrega, on_delete=models.CASCADE, related_name='historico')
    data_evento = models.DateTimeField(auto_now_add=True)
    descricao = models.CharField(max_length=255)
    localizacao = models.ForeignKey(Coordenada, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-data_evento']

    def __str__(self):
        return f"{self.data_evento.strftime('%d/%m/%Y %H:%M')} - {self.descricao}"
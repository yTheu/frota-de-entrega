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
                veiculo_disponivel = Veiculo.objects.select_for_update().filter(status='DISPONIVEL').first()
                motorista_disponivel = PerfilMotorista.objects.select_for_update().filter(disponivel=True).first()

                if not veiculo_disponivel or not motorista_disponivel:
                    return (False, "Nenhum veículo ou motorista disponível no momento.")
                
                inicio_previsto = timezone.now() + timezone.timedelta(minutes=15)
                fim_previsto = inicio_previsto + timezone.timedelta(minutes=dados_api['duracao_minutos'])

                #cria rota
                nova_rota = self.model.objects.create(
                    veiculo=veiculo_disponivel,
                    motorista=motorista_disponivel,
                    status='PLANEJADA',
                    distancia_total_km=dados_api['distancia_km'],
                    duracao_estimada_minutos=dados_api['duracao_minutos'],
                    data_inicio_prevista=inicio_previsto,
                    data_fim_prevista=fim_previsto
                )

                #associa entregas à rota
                entregas_alocar = Entrega.objects.filter(id__in=ids_entregas, status='PENDENTE')
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

    data_inicio_prevista = models.DateTimeField(null=True, blank=True)
    data_fim_prevista = models.DateTimeField(null=True, blank=True)    

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

    def __str__(self):
        return f"{self.latitude}, {self.longitude}"

class Entrega(models.Model):
    STATUS_ENTREGA = [
        ("PENDENTE", "Pendente"),
        ("EM_SEPARACAO", "Em Separação"),
        ("EM_ROTA", "Em Rota"),
        ("ENTREGUE", "Entregue"),
        ("PROBLEMA", "Problema"),
    ]

    origem = models.ForeignKey(Coordenada, on_delete=models.SET_NULL, null=True, related_name="origens")
    destino = models.ForeignKey(Coordenada, on_delete=models.SET_NULL, null=True, related_name="destinos")
    status = models.CharField(max_length=20, choices=STATUS_ENTREGA, default="PENDENTE")
    cliente = models.ForeignKey(PerfilCliente, on_delete=models.SET_NULL, null=True, blank=True)
    rota = models.ForeignKey(Rota, on_delete=models.SET_NULL, null=True, blank=True, related_name='entregas')

    data_entrega_prevista = models.DateTimeField()
    data_entrega_real = models.DateTimeField(null=True, blank=True)

    def verificar_disponibilidade_rota(self):
        if self.rota and self.rota.veiculo and self.rota.veiculo.status != 'DISPONIVEL':
            raise ValidationError(f'O veículo {self.rota.veiculo.modelo} - {self.rota.veiculo.placa} da rota não está disponível!')
        
    def __str__(self):
        return f"Entrega #{self.id} para {self.cliente}"